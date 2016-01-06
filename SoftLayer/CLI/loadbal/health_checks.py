"""List health check types."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting


@click.command()
@environment.pass_env
def cli(env):
    """List health check types."""

    mgr = SoftLayer.LoadBalancerManager(env.client)

    hc_types = mgr.get_hc_types()
    table = formatting.KeyValueTable(['ID', 'Name'])
    table.align['ID'] = 'l'
    table.align['Name'] = 'l'
    table.sortby = 'ID'
    for hc_type in hc_types:
        table.add_row([hc_type['id'], hc_type['name']])

    env.fout(table)
