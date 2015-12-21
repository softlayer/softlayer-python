"""Edit the properties of a service group."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import loadbal


@click.command()
@click.argument('identifier')
@click.option('--enabled / --disabled',
              default=None,
              help="Enable or disable the service")
@click.option('--port',
              help="Change the port number for the service", type=click.INT)
@click.option('--weight',
              type=click.INT,
              help="Change the weight of the service")
@click.option('--healthcheck-type', help="Change the health check type")
@click.option('--ip-address', help="Change the IP address of the service")
@environment.pass_env
def cli(env, identifier, enabled, port, weight, healthcheck_type, ip_address):
    """Edit the properties of a service group."""

    mgr = SoftLayer.LoadBalancerManager(env.client)

    loadbal_id, service_id = loadbal.parse_id(identifier)

    # check if any input is provided
    if ((not any([ip_address, weight, port, healthcheck_type])) and
            enabled is None):
        raise exceptions.CLIAbort(
            'At least one property is required to be changed!')

    # check if the IP is valid
    ip_address_id = None
    if ip_address:
        ip_service = env.client['Network_Subnet_IpAddress']
        ip_record = ip_service.getByIpAddress(ip_address)
        ip_address_id = ip_record['id']

    mgr.edit_service(loadbal_id,
                     service_id,
                     ip_address_id=ip_address_id,
                     enabled=enabled,
                     port=port,
                     weight=weight,
                     hc_type=healthcheck_type)
    env.fout('Load balancer service %s is being modified!' % identifier)
