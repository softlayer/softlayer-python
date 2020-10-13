"""Manage LBaaS health checks."""
import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.exceptions import SoftLayerAPIError
from SoftLayer import utils


@click.command()
@click.argument('identifier')
@click.option('--uuid', required=True, help="Health check UUID to modify.")
@click.option('--interval', '-i', type=click.IntRange(2, 60), help="Seconds between checks. [2-60]")
@click.option('--retry', '-r', type=click.IntRange(1, 10), help="Number of times before marking as DOWN. [1-10]")
@click.option('--timeout', '-t', type=click.IntRange(1, 59), help="Seconds to wait for a connection. [1-59]")
@click.option('--url', '-u', help="Url path for HTTP/HTTPS checks.")
@environment.pass_env
def cli(env, identifier, uuid, interval, retry, timeout, url):
    """Manage LBaaS health checks."""

    if not any([interval, retry, timeout, url]):
        raise exceptions.ArgumentError("Specify either interval, retry, timeout, url")

    # map parameters to expected API names
    template = {'healthMonitorUuid': uuid, 'interval': interval,
                'maxRetries': retry, 'timeout': timeout, 'urlPath': url}
    # Removes those empty values
    clean_template = {k: v for k, v in template.items() if v is not None}

    mgr = SoftLayer.LoadBalancerManager(env.client)
    # Need to get the LBaaS uuid if it wasn't supplied
    lb_uuid, lb_id = mgr.get_lbaas_uuid_id(identifier)
    print("UUID: {}, ID: {}".format(lb_uuid, lb_id))

    # Get the current health checks, and find the one we are updating.
    mask = "mask[healthMonitors, listeners[uuid,defaultPool[healthMonitor]]]"
    lbaas = mgr.get_lb(lb_id, mask=mask)

    check = {}
    # Set the default values, because these all need to be set if we are not updating them.
    for listener in lbaas.get('listeners', []):
        if utils.lookup(listener, 'defaultPool', 'healthMonitor', 'uuid') == uuid:
            check['backendProtocol'] = utils.lookup(listener, 'defaultPool', 'protocol')
            check['backendPort'] = utils.lookup(listener, 'defaultPool', 'protocolPort')
            check['healthMonitorUuid'] = uuid
            check['interval'] = utils.lookup(listener, 'defaultPool', 'healthMonitor', 'interval')
            check['maxRetries'] = utils.lookup(listener, 'defaultPool', 'healthMonitor', 'maxRetries')
            check['timeout'] = utils.lookup(listener, 'defaultPool', 'healthMonitor', 'timeout')
            check['urlPath'] = utils.lookup(listener, 'defaultPool', 'healthMonitor', 'urlPath')

    if url and check['backendProtocol'] == 'TCP':
        raise exceptions.ArgumentError('--url cannot be used with TCP checks')

    # Update existing check with supplied values
    for key in clean_template.keys():
        check[key] = clean_template[key]

    try:
        mgr.update_lb_health_monitors(lb_uuid, [check])
        click.secho('Health Check {} updated successfully'.format(uuid), fg='green')
    except SoftLayerAPIError as exception:
        click.secho('Failed to update {}'.format(uuid), fg='red')
        click.secho("ERROR: {}".format(exception.faultString), fg='red')
