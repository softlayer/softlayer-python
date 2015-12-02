"""List routing methods."""
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

    routing_methods = mgr.get_routing_methods()
    table = formatting.KeyValueTable(['ID', 'Name'])
    table.align['ID'] = 'l'
    table.align['Name'] = 'l'
    table.sortby = 'ID'
    for routing_method in routing_methods:
        table.add_row([routing_method['id'], routing_method['name']])

    env.fout(table)
