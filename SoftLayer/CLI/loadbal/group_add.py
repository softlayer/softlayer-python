"""Adds a new load_balancer service."""
# :license: MIT, see LICENSE for more details.

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import loadbal

import click


@click.command()
@click.argument('identifier')
@click.option('--allocation',
              required=True,
              type=click.INT,
              help="The allocated percent of connections")
@click.option('--port',
              required=True,
              help="The port number",
              type=click.INT)
@click.option('--routing-type',
              required=True,
              help="The port routing type")
@click.option('--routing-method',
              required=True,
              help="The routing method")
@environment.pass_env
def cli(env, identifier, allocation, port, routing_type, routing_method):
    """Adds a new load_balancer service."""

    mgr = SoftLayer.LoadBalancerManager(env.client)

    _, loadbal_id = loadbal.parse_id(identifier)

    mgr.add_service_group(loadbal_id,
                          allocation=allocation,
                          port=port,
                          routing_type=routing_type,
                          routing_method=routing_method)

    return 'Load balancer service group is being added!'
