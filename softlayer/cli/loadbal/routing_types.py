"""List routing types."""
# :license: MIT, see LICENSE for more details.

import softlayer
from softlayer.cli import environment
from softlayer.cli import formatting

import click


@click.command()
@environment.pass_env
def cli(env):
    """List routing types."""
    mgr = softlayer.LoadBalancerManager(env.client)

    routing_methods = mgr.get_routing_methods()
    table = formatting.KeyValueTable(['ID', 'Name'])
    table.align['ID'] = 'l'
    table.align['Name'] = 'l'
    table.sortby = 'ID'
    for routing_method in routing_methods:
        table.add_row([routing_method['id'], routing_method['name']])
    return table
