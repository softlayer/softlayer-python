"""List routing types."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting


@click.command()
@environment.pass_env
def cli(env):
    """List routing types."""
    mgr = SoftLayer.LoadBalancerManager(env.client)

    routing_types = mgr.get_routing_types()
    table = formatting.KeyValueTable(['ID', 'Name'])
    table.align['ID'] = 'l'
    table.align['Name'] = 'l'
    table.sortby = 'ID'
    for routing_type in routing_types:
        table.add_row([routing_type['id'], routing_type['name']])
    env.fout(table)
