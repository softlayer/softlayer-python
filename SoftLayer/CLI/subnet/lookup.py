"""Find an IP address and display its subnet and device info."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting


@click.command()
@click.argument('ip_address')
@environment.pass_env
def cli(env, ip_address):
    """Find an IP address and display its subnet and device info."""

    mgr = SoftLayer.NetworkManager(env.client)

    addr_info = mgr.ip_lookup(ip_address)

    if not addr_info:
        raise exceptions.CLIAbort('Not found')

    table = formatting.KeyValueTable(['name', 'value'])
    table.align['name'] = 'r'
    table.align['value'] = 'l'

    table.add_row(['id', addr_info['id']])
    table.add_row(['ip', addr_info['ipAddress']])

    subnet_table = formatting.KeyValueTable(['name', 'value'])
    subnet_table.align['name'] = 'r'
    subnet_table.align['value'] = 'l'
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
        device_table = formatting.KeyValueTable(['name', 'value'])
        device_table.align['name'] = 'r'
        device_table.align['value'] = 'l'
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
    env.fout(table)
