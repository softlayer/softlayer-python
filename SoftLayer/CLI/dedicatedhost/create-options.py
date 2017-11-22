"""Options for ordering a dedicated host"""
# :license: MIT, see LICENSE for more details.

import click
import SoftLayer

from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting


@click.command()
@environment.pass_env
def cli(env):
    """host order options for a given dedicated host."""

    mgr = SoftLayer.DedicatedHostManager(env.client)
    options = mgr.get_create_options()

    tables = []

    # Datacenters
    dc_table = formatting.Table(['datacenter', 'value'])
    dc_table.sortby = 'value'
    for location in options['locations']:
        dc_table.add_row([location['name'], location['key']])
    tables.append(dc_table)

    dh_table = formatting.Table(['dedicated Virtual Host', 'value'])
    dh_table.sortby = 'value'
    for item in options['dedicated_host']:
        dh_table.add_row([item['name'], item['key']])
    tables.append(dh_table)

    env.fout(formatting.listing(tables, separator='\n'))
