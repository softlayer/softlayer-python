"""List subnets."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer import utils


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.option('--sortby',
              help='Column to sort by',
              type=click.Choice(['id',
                                 'identifier',
                                 'type',
                                 'network_space',
                                 'datacenter',
                                 'vlan_id',
                                 'IPs',
                                 'hardware',
                                 'vs']))
@environment.pass_env
def cli(env, sortby):
    """List subnets."""

    mgr = SoftLayer.NetworkManager(env.client)

    table = formatting.Table([
        'id', 'identifier', 'type', 'network_space', 'datacenter', 'vlan_id',
        'IPs', 'hardware', 'vs',
    ])
    table.sortby = sortby

    subnets = mgr.list_subnets()

    for subnet in subnets:
        table.add_row([
            subnet['id'],
            '%s/%s' % (subnet['networkIdentifier'], str(subnet['cidr'])),
            subnet.get('subnetType', formatting.blank()),
            utils.lookup(subnet,
                         'networkVlan',
                         'networkSpace') or formatting.blank(),
            utils.lookup(subnet, 'datacenter', 'name', ) or formatting.blank(),
            subnet['networkVlanId'],
            subnet['ipAddressCount'],
            len(subnet['hardware']),
            len(subnet['virtualGuests']),
        ])

    env.fout(table)
