"""List VLANs."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer import utils

COLUMNS = ['id',
           'number',
           'name',
           'firewall',
           'datacenter',
           'hardware',
           'virtual_servers',
           'public_ips']


@click.command()
@click.option('--sortby',
              help='Column to sort by',
              type=click.Choice(COLUMNS))
@click.option('--datacenter', '-d',
              help='Filter by datacenter shortname (sng01, dal05, ...)')
@click.option('--number', '-n', help='Filter by VLAN number')
@click.option('--name', help='Filter by VLAN name')
@click.option('--limit', '-l',
              help='How many results to get in one api call, default is 100',
              default=100,
              show_default=True)
@environment.pass_env
def cli(env, sortby, datacenter, number, name, limit):
    """List VLANs."""

    mgr = SoftLayer.NetworkManager(env.client)

    table = formatting.Table(COLUMNS)
    table.sortby = sortby

    vlans = mgr.list_vlans(datacenter=datacenter,
                           vlan_number=number,
                           name=name,
                           limit=limit)
    for vlan in vlans:
        table.add_row([
            vlan['id'],
            vlan['vlanNumber'],
            vlan.get('name') or formatting.blank(),
            'Yes' if vlan['firewallInterfaces'] else 'No',
            utils.lookup(vlan, 'primaryRouter', 'datacenter', 'name'),
            vlan['hardwareCount'],
            vlan['virtualGuestCount'],
            vlan['totalPrimaryIpAddressCount'],
        ])

    env.fout(table)
