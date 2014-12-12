"""Get details about a VLAN."""
# :license: MIT, see LICENSE for more details.

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers


import click


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

    table = formatting.KeyValueTable(['Name', 'Value'])
    table.align['Name'] = 'r'
    table.align['Value'] = 'l'

    table.add_row(['id', vlan['id']])
    table.add_row(['number', vlan['vlanNumber']])
    table.add_row(['datacenter',
                   vlan['primaryRouter']['datacenter']['longName']])
    table.add_row(['primary router',
                   vlan['primaryRouter']['fullyQualifiedDomainName']])
    table.add_row(['firewall',
                   'Yes' if vlan['firewallInterfaces'] else 'No'])
    subnets = []
    for subnet in vlan['subnets']:
        subnet_table = formatting.KeyValueTable(['Name', 'Value'])
        subnet_table.align['Name'] = 'r'
        subnet_table.align['Value'] = 'l'
        subnet_table.add_row(['id', subnet['id']])
        subnet_table.add_row(['identifier', subnet['networkIdentifier']])
        subnet_table.add_row(['netmask', subnet['netmask']])
        subnet_table.add_row(['gateway', subnet.get('gateway', '-')])
        subnet_table.add_row(['type', subnet['subnetType']])
        subnet_table.add_row(['usable ips',
                              subnet['usableIpAddressCount']])
        subnets.append(subnet_table)

    table.add_row(['subnets', subnets])

    if not no_vs:
        if vlan['virtualGuests']:
            vs_table = formatting.KeyValueTable(['Hostname',
                                                 'Domain',
                                                 'IP'])
            vs_table.align['Hostname'] = 'r'
            vs_table.align['IP'] = 'l'
            for vsi in vlan['virtualGuests']:
                vs_table.add_row([vsi['hostname'],
                                  vsi['domain'],
                                  vsi.get('primaryIpAddress')])
            table.add_row(['vs', vs_table])
        else:
            table.add_row(['vs', 'none'])

    if not no_hardware:
        if vlan['hardware']:
            hw_table = formatting.Table(['Hostname', 'Domain', 'IP'])
            hw_table.align['Hostname'] = 'r'
            hw_table.align['IP'] = 'l'
            for hardware in vlan['hardware']:
                hw_table.add_row([hardware['hostname'],
                                  hardware['domain'],
                                  hardware.get('primaryIpAddress')])
            table.add_row(['hardware', hw_table])
        else:
            table.add_row(['hardware', 'none'])

    return table
