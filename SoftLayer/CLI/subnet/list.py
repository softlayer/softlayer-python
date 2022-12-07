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
        'Id', 'Identifier', 'Network', 'Type', 'VLAN', 'Location', 'Target',
        'IPs', 'Hardware', 'Vs', 'Tags', 'Note'
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
        subnet_type = subnet.get('subnetType', formatting.blank())
        if subnet_type == 'PRIMARY' or subnet_type == 'PRIMARY_6' or subnet_type == 'ADDITIONAL_PRIMARY':
            subnet_type = 'Primary'
        if subnet_type == 'SECONDARY_ON_VLAN':
            subnet_type = 'Portable'
        if subnet_type == 'STATIC_IP_ROUTED':
            subnet_type = 'Static'
        if subnet_type == 'GLOBAL_IP':
            subnet_type = 'Global'

        network = subnet.get('addressSpace', formatting.blank())
        if network is not None:
            network = str(network).capitalize()

        vlan = utils.lookup(subnet, 'networkVlan', 'fullyQualifiedName')
        if vlan is None:
            vlan = 'Unrouted'
        table.add_row([
            subnet['id'],
            '%s/%s' % (subnet['networkIdentifier'], str(subnet['cidr'])),
            network,
            subnet_type,
            vlan,
            utils.lookup(subnet, 'datacenter', 'name') or formatting.blank(),
            utils.lookup(subnet, 'endPointIpAddress', 'ipAddress') or formatting.blank(),
            subnet['ipAddressCount'],
            len(subnet['hardware']),
            len(subnet['virtualGuests']),
            formatting.tags(subnet.get('tagReferences')),
            utils.lookup(subnet, 'note') or formatting.blank(),
        ])

    env.fout(table)
