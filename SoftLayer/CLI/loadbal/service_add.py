"""Adds a new load balancer service."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import loadbal


@click.command()
@click.argument('identifier')
@click.option('--enabled / --disabled',
              required=True,
              help="Create the service as enabled or disabled")
@click.option('--port',
              required=True,
              help="The port number for the service",
              type=click.INT)
@click.option('--weight',
              required=True,
              type=click.INT,
              help="The weight of the service")
@click.option('--healthcheck-type',
              required=True,
              help="The health check type")
@click.option('--ip-address',
              required=True,
              help="The IP address of the service")
@environment.pass_env
def cli(env, identifier, enabled, port, weight, healthcheck_type, ip_address):
    """Adds a new load balancer service."""

    mgr = SoftLayer.LoadBalancerManager(env.client)

    loadbal_id, group_id = loadbal.parse_id(identifier)

    # check if the IP is valid
    ip_address_id = None
    if ip_address:
        ip_service = env.client['Network_Subnet_IpAddress']
        ip_record = ip_service.getByIpAddress(ip_address)
        if len(ip_record) > 0:
            ip_address_id = ip_record['id']

    mgr.add_service(loadbal_id,
                    group_id,
                    ip_address_id=ip_address_id,
                    enabled=enabled,
                    port=port,
                    weight=weight,
                    hc_type=healthcheck_type)
    env.fout('Load balancer service is being added!')
