"""Options for ordering a dedicated host"""
# :license: MIT, see LICENSE for more details.

import click
import SoftLayer

from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting


@click.command()
@click.option('--datacenter', '-d',
              help="Router hostname (requires --flavor) "
                   "ex. ams01",
              show_default=True)
@click.option('--flavor', '-f',
              help="Dedicated Virtual Host flavor (requires --datacenter)"
                   " ex. 56_CORES_X_242_RAM_X_1_4_TB",
              show_default=True)
@environment.pass_env
def cli(env, **kwargs):
    """host order options for a given dedicated host.

    To get a list of available backend routers see example:
    slcli dh create-options --datacenter dal05 --flavor 56_CORES_X_242_RAM_X_1_4_TB
    """

    mgr = SoftLayer.DedicatedHostManager(env.client)
    tables = []

    if not kwargs['flavor'] and not kwargs['datacenter']:
        options = mgr.get_create_options()

        # Datacenters
        dc_table = formatting.Table(['datacenter', 'value'])
        dc_table.sortby = 'value'
        for location in options['locations']:
            dc_table.add_row([location['name'], location['key']])
        tables.append(dc_table)

        dh_table = formatting.Table(['Dedicated Virtual Host Flavor(s)', 'value'])
        dh_table.sortby = 'value'
        for item in options['dedicated_host']:
            dh_table.add_row([item['name'], item['key']])
        tables.append(dh_table)
    else:
        if kwargs['flavor'] is None or kwargs['datacenter'] is None:
            raise exceptions.ArgumentError('Both a flavor and datacenter need '
                                           'to be passed as arguments '
                                           'ex. slcli dh create-options -d '
                                           'ams01 -f '
                                           '56_CORES_X_242_RAM_X_1_4_TB')
        router_opt = mgr.get_router_options(kwargs['datacenter'], kwargs['flavor'])
        br_table = formatting.Table(
            ['Available Backend Routers'])
        for router in router_opt:
            br_table.add_row([router['hostname']])
        tables.append(br_table)

    env.fout(formatting.listing(tables, separator='\n'))
