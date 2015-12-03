"""Edit an existing load balancer service group."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import loadbal


@click.command()
@click.argument('identifier')
@click.option('--allocation',
              type=click.INT,
              help="Change the allocated percent of connections")
@click.option('--port',
              help="Change the port number",
              type=click.INT)
@click.option('--routing-type',
              help="Change the port routing type")
@click.option('--routing-method',
              help="Change the routing method")
@environment.pass_env
def cli(env, identifier, allocation, port, routing_type, routing_method):
    """Edit an existing load balancer service group."""
    mgr = SoftLayer.LoadBalancerManager(env.client)

    loadbal_id, group_id = loadbal.parse_id(identifier)

    # check if any input is provided
    if not any([allocation, port, routing_type, routing_method]):
        raise exceptions.CLIAbort(
            'At least one property is required to be changed!')

    mgr.edit_service_group(loadbal_id,
                           group_id,
                           allocation=allocation,
                           port=port,
                           routing_type=routing_type,
                           routing_method=routing_method)

    env.fout('Load balancer service group %s is being updated!' % identifier)
