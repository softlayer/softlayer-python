"""List VLANs."""
# :license: MIT, see LICENSE for more details.

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer import utils


import click


@click.command()
@click.option('--sortby',
              help='Column to sort by',
              type=click.Choice(['id',
                                 'number',
                                 'datacenter',
                                 'IPs',
                                 'hardware',
                                 'vs',
                                 'networking',
                                 'firewall']))
@click.option('--datacenter', '-d',
              help='Filter by datacenter shortname (sng01, dal05, ...)')
@click.option('--number', '-n', help='Filter by VLAN number')
@click.option('--name', help='Filter by VLAN name')
@environment.pass_env
def cli(env, sortby, datacenter, number, name):
    """List VLANs."""

    mgr = SoftLayer.NetworkManager(env.client)

    table = formatting.Table([
        'id', 'number', 'datacenter', 'name', 'IPs', 'hardware', 'vs',
        'networking', 'firewall'
    ])
    table.sortby = sortby

    vlans = mgr.list_vlans(datacenter=datacenter,
                           vlan_number=number,
                           name=name)
    for vlan in vlans:
        table.add_row([
            vlan['id'],
            vlan['vlanNumber'],
            utils.lookup(vlan, 'primaryRouter', 'datacenter', 'name'),
            vlan.get('name') or formatting.blank(),
            vlan['totalPrimaryIpAddressCount'],
            len(vlan['hardware']),
            len(vlan['virtualGuests']),
            len(vlan['networkComponents']),
            'Yes' if vlan['firewallInterfaces'] else 'No',
        ])

    return table
