"""List health check types."""
# :license: MIT, see LICENSE for more details.

import softlayer
from softlayer.cli import environment
from softlayer.cli import formatting

import click


@click.command()
@environment.pass_env
def cli(env):
    """List health check types."""

    mgr = softlayer.LoadBalancerManager(env.client)

    hc_types = mgr.get_hc_types()
    table = formatting.KeyValueTable(['ID', 'Name'])
    table.align['ID'] = 'l'
    table.align['Name'] = 'l'
    table.sortby = 'ID'
    for hc_type in hc_types:
        table.add_row([hc_type['id'], hc_type['name']])

    return table
