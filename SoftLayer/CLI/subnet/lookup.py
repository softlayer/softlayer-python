"""Find an IP address and display its subnet and device info."""
# :license: MIT, see LICENSE for more details.

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting


import click


@click.command()
@click.argument('ip_address')
@environment.pass_env
def cli(env, ip_address):
    """Find an IP address and display its subnet and device info."""

    mgr = SoftLayer.NetworkManager(env.client)

    addr_info = mgr.ip_lookup(ip_address)

    if not addr_info:
        return 'Not found'

    table = formatting.KeyValueTable(['Name', 'Value'])
    table.align['Name'] = 'r'
    table.align['Value'] = 'l'

    table.add_row(['id', addr_info['id']])
    table.add_row(['ip', addr_info['ipAddress']])

    subnet_table = formatting.KeyValueTable(['Name', 'Value'])
    subnet_table.align['Name'] = 'r'
    subnet_table.align['Value'] = 'l'
    subnet_table.add_row(['id', addr_info['subnet']['id']])
    subnet_table.add_row(['identifier',
                          '%s/%s' % (addr_info['subnet']['networkIdentifier'],
                                     str(addr_info['subnet']['cidr']))])
    subnet_table.add_row(['netmask', addr_info['subnet']['netmask']])
    if addr_info['subnet'].get('gateway'):
        subnet_table.add_row(['gateway', addr_info['subnet']['gateway']])
    subnet_table.add_row(['type', addr_info['subnet'].get('subnetType')])

    table.add_row(['subnet', subnet_table])

    if addr_info.get('virtualGuest') or addr_info.get('hardware'):
        device_table = formatting.KeyValueTable(['Name', 'Value'])
        device_table.align['Name'] = 'r'
        device_table.align['Value'] = 'l'
        if addr_info.get('virtualGuest'):
            device = addr_info['virtualGuest']
            device_type = 'vs'
        else:
            device = addr_info['hardware']
            device_type = 'server'
        device_table.add_row(['id', device['id']])
        device_table.add_row(['name', device['fullyQualifiedDomainName']])
        device_table.add_row(['type', device_type])
        table.add_row(['device', device_table])
    return table
