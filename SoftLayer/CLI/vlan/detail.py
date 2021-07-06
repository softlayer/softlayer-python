"""Get details about a VLAN."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers
from SoftLayer import utils


@click.command()
@click.argument('identifier')
@click.option('--no-vs',
              is_flag=True,
              help="Hide virtual server listing")
@click.option('--no-hardware',
              is_flag=True,
              help="Hide hardware listing")
@environment.pass_env
def cli(env, identifier, no_vs, no_hardware):
    """Get details about a VLAN."""

    mgr = SoftLayer.NetworkManager(env.client)

    vlan_id = helpers.resolve_id(mgr.resolve_vlan_ids, identifier, 'VLAN')
    vlan = mgr.get_vlan(vlan_id)

    table = formatting.KeyValueTable(['name', 'value'])
    table.align['name'] = 'r'
    table.align['value'] = 'l'

    table.add_row(['id', vlan.get('id')])
    table.add_row(['number', vlan.get('vlanNumber')])
    table.add_row(['datacenter',
                   utils.lookup(vlan, 'primaryRouter', 'datacenter', 'longName')])
    table.add_row(['primary_router',
                   utils.lookup(vlan, 'primaryRouter', 'fullyQualifiedDomainName')])
    table.add_row(['Gateway/Firewall', get_gateway_firewall(vlan)])
    subnets = []
    for subnet in vlan.get('subnets', []):
        subnet_table = formatting.KeyValueTable(['name', 'value'])
        subnet_table.align['name'] = 'r'
        subnet_table.align['value'] = 'l'
        subnet_table.add_row(['id', subnet.get('id')])
        subnet_table.add_row(['identifier', subnet.get('networkIdentifier')])
        subnet_table.add_row(['netmask', subnet.get('netmask')])
        subnet_table.add_row(['gateway', subnet.get('gateway', formatting.blank())])
        subnet_table.add_row(['type', subnet.get('subnetType')])
        subnet_table.add_row(['usable ips', subnet.get('usableIpAddressCount')])
        subnets.append(subnet_table)

    table.add_row(['subnets', subnets])

    server_columns = ['hostname', 'domain', 'public_ip', 'private_ip']

    if not no_vs:
        if vlan.get('virtualGuests'):
            vs_table = formatting.KeyValueTable(server_columns)
            for vsi in vlan['virtualGuests']:
                vs_table.add_row([vsi.get('hostname'),
                                  vsi.get('domain'),
                                  vsi.get('primaryIpAddress'),
                                  vsi.get('primaryBackendIpAddress')])
            table.add_row(['vs', vs_table])
        else:
            table.add_row(['vs', 'none'])

    if not no_hardware:
        if vlan.get('hardware'):
            hw_table = formatting.Table(server_columns)
            for hardware in vlan['hardware']:
                hw_table.add_row([hardware.get('hostname'),
                                  hardware.get('domain'),
                                  hardware.get('primaryIpAddress'),
                                  hardware.get('primaryBackendIpAddress')])
            table.add_row(['hardware', hw_table])
        else:
            table.add_row(['hardware', 'none'])

    env.fout(table)


def get_gateway_firewall(vlan):
    """Gets the name of a gateway/firewall from a VLAN. """

    firewall = utils.lookup(vlan, 'networkVlanFirewall', 'fullyQualifiedDomainName')
    if firewall:
        return firewall
    gateway = utils.lookup(vlan, 'attachedNetworkGateway', 'name')
    if gateway:
        return gateway
    return formatting.blank()
