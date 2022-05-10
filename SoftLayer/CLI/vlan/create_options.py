"""Vlan order options."""
# :license: MIT, see LICENSE for more details.
# pylint: disable=too-many-statements
import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting


@click.command(cls=SoftLayer.CLI.command.SLCommand, short_help="Get options to use for creating Vlan servers.")
@environment.pass_env
def cli(env):
    """List all the options for creating VLAN"""

    mgr = SoftLayer.NetworkManager(env.client)
    datacenters = mgr.get_list_datacenter()

    table = formatting.Table(['Options', 'Value'], title="Datacenters")
    router_table = formatting.Table(['Datacenter', 'Router/Pod'])
    dc_table = formatting.Table(['Datacenters'])
    table.add_row(['VLAN type', 'Private, Public'])

    for datacenter in datacenters:
        dc_table.add_row([datacenter['name']])
        routers = mgr.get_routers(datacenter['id'])
        for router in routers:
            router_table.add_row([datacenter['name'], router['hostname']])

    table.add_row(['Datacenters', dc_table])
    table.add_row(['Routers', router_table])

    env.fout(table)
