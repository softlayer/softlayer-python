"""Manage LBaaS Pools/Listeners."""
import click

import SoftLayer
from SoftLayer.CLI import environment, formatting, helpers
from SoftLayer.exceptions import SoftLayerAPIError
from SoftLayer import utils
from pprint import pprint as pp 


def sticky_option(ctx, param, value):
    if value:
        return 'SOURCE_IP'
    return None

@click.command()
@click.argument('identifier')
@click.option('--frontProtocol', '-P', default='HTTP',  type=click.Choice(['HTTP', 'HTTPS', 'TCP']), show_default=True,
              help="Protocol type to use for incoming connections")
@click.option('--backProtocol', '-p', type=click.Choice(['HTTP', 'HTTPS', 'TCP']),
              help="Protocol type to use when connecting to backend servers. Defaults to whatever --frontProtocol is.")
@click.option('--frontPort', '-f',  required=True, type=int, help="Internet side port")
@click.option('--backPort', '-b',  required=True, type=int, help="Private side port")
@click.option('--method', '-m',  default='ROUNDROBIN', show_default=True, help="Balancing Method",
              type=click.Choice(['ROUNDROBIN', 'LEASTCONNECTION', 'WEIGHTED_RR']))
@click.option('--connections', '-c', type=int, help="Maximum number of connections to allow.")
@click.option('--sticky', '-s', is_flag=True, callback=sticky_option, help="Make sessions sticky based on source_ip.")
@environment.pass_env
def add(env, identifier,  **args):
    """Adds a listener to the identifier LB"""

    mgr = SoftLayer.LoadBalancerManager(env.client)
    uuid, lbid = mgr.get_lbaas_uuid_id(identifier)

    new_listener = {
        'backendPort': args.get('backport'),
        'backendProtocol': args.get('backprotocol') if args.get('backprotocol') else args.get('frontprotocol'),
        'frontendPort': args.get('frontport'),
        'frontendProtocol': args.get('frontprotocol'),
        'loadBalancingMethod': args.get('method'),
        'maxConn': args.get('connections', None),
        'sessionType': args.get('sticky'),
        'tlsCertificateId': None
    }

    try:
        result = mgr.add_lb_listener(uuid, new_listener)
        click.secho("Success", fg='green')
    except SoftLayerAPIError as e:
        click.secho("ERROR: {}".format(e.faultString), fg='red')


@click.command()
@click.argument('identifier')
@click.argument('listener')
@click.option('--frontProtocol', '-P', type=click.Choice(['HTTP', 'HTTPS', 'TCP']),
              help="Protocol type to use for incoming connections")
@click.option('--backProtocol', '-p', type=click.Choice(['HTTP', 'HTTPS', 'TCP']),
              help="Protocol type to use when connecting to backend servers. Defaults to whatever --frontProtocol is.")
@click.option('--frontPort', '-f',  type=int, help="Internet side port")
@click.option('--backPort', '-b', type=int, help="Private side port")
@click.option('--method', '-m', help="Balancing Method",
              type=click.Choice(['ROUNDROBIN', 'LEASTCONNECTION', 'WEIGHTED_RR']))
@click.option('--connections', '-c', type=int, help="Maximum number of connections to allow.")
@click.option('--sticky', '-s', is_flag=True, callback=sticky_option, help="Make sessions sticky based on source_ip.")
@environment.pass_env
def edit(env, identifier, listener, **args):
    """Updates a listener's configuration. 

    LISTENER should be a UUID, and can be found from `slcli lb detail <IDENTIFIER>`
    """

    mgr = SoftLayer.LoadBalancerManager(env.client)
    uuid, lbid = mgr.get_lbaas_uuid_id(identifier)


    new_listener = {
        'listenerUuid': listener
    }

    arg_to_option = {
        'frontprotocol': 'frontendProtocol',
        'backprotocol': 'backendProtocol',
        'frontport': 'frontendPort',
        'backport': 'backendPort',
        'method': 'loadBalancingMethod',
        'connections': 'maxConn',
        'sticky': 'sessionType',
        'sslcert': 'tlsCertificateId'
    }

    for arg in args.keys():
        if args[arg]:
            new_listener[arg_to_option[arg]] = args[arg]

    try:
        result = mgr.add_lb_listener(uuid, new_listener)
        click.secho("Success", fg='green')
    except SoftLayerAPIError as e:
        click.secho("ERROR: {}".format(e.faultString), fg='red')


@click.command()
@click.argument('identifier')
@click.argument('listener')
@environment.pass_env
def delete(env, identifier, listener):
    """Removes the listener from identified LBaaS instance
    
    LISTENER should be a UUID, and can be found from `slcli lb detail <IDENTIFIER>`
    """

    mgr = SoftLayer.LoadBalancerManager(env.client)
    uuid, lbid = mgr.get_lbaas_uuid_id(identifier)
    try:
        result = mgr.remove_lb_listener(uuid, listener)
        click.secho("Success", fg='green')
    except SoftLayerAPIError as e:
        click.secho("ERROR: {}".format(e.faultString), fg='red')