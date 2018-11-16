"""List subnets."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer import utils


@click.command()
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
@click.option('--datacenter', '-d',
              help="Filter by datacenter shortname (sng01, dal05, ...)")
@click.option('--identifier', help="Filter by network identifier")
@click.option('--subnet-type', '-t', help="Filter by subnet type")
@click.option('--network-space', help="Filter by network space")
@click.option('--ipv4', '--v4', is_flag=True, help="Display only IPv4 subnets")
@click.option('--ipv6', '--v6', is_flag=True, help="Display only IPv6 subnets")
@environment.pass_env
def cli(env, sortby, datacenter, identifier, subnet_type, network_space, ipv4, ipv6):
    """List subnets."""

    mgr = SoftLayer.NetworkManager(env.client)

    table = formatting.Table([
        'id', 'identifier', 'type', 'network_space', 'datacenter', 'vlan_id',
        'IPs', 'hardware', 'vs',
    ])
    table.sortby = sortby

    version = 0
    if ipv4:
        version = 4
    elif ipv6:
        version = 6

    subnets = mgr.list_subnets(
        datacenter=datacenter,
        version=version,
        identifier=identifier,
        subnet_type=subnet_type,
        network_space=network_space,
    )

    for subnet in subnets:
        table.add_row([
            subnet['id'],
            '%s/%s' % (subnet['networkIdentifier'], str(subnet['cidr'])),
            subnet.get('subnetType', formatting.blank()),
            utils.lookup(subnet,
                         'networkVlan',
                         'networkSpace') or formatting.blank(),
            utils.lookup(subnet, 'datacenter', 'name',) or formatting.blank(),
            subnet['networkVlanId'],
            subnet['ipAddressCount'],
            len(subnet['hardware']),
            len(subnet['virtualGuests']),
        ])

    env.fout(table)
