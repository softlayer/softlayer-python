"""Get details about a VLAN."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers


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

    table.add_row(['id', vlan['id']])
    table.add_row(['number', vlan['vlanNumber']])
    table.add_row(['datacenter',
                   vlan['primaryRouter']['datacenter']['longName']])
    table.add_row(['primary_router',
                   vlan['primaryRouter']['fullyQualifiedDomainName']])
    table.add_row(['firewall',
                   'Yes' if vlan['firewallInterfaces'] else 'No'])
    subnets = []
    for subnet in vlan.get('subnets', []):
        subnet_table = formatting.KeyValueTable(['name', 'value'])
        subnet_table.align['name'] = 'r'
        subnet_table.align['value'] = 'l'
        subnet_table.add_row(['id', subnet['id']])
        subnet_table.add_row(['identifier', subnet['networkIdentifier']])
        subnet_table.add_row(['netmask', subnet['netmask']])
        subnet_table.add_row(['gateway', subnet.get('gateway', '-')])
        subnet_table.add_row(['type', subnet['subnetType']])
        subnet_table.add_row(['usable ips',
                              subnet['usableIpAddressCount']])
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
