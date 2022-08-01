"""List  User Device access."""
import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """User Device access."""

    mgr = SoftLayer.UserManager(env.client)
    all_permissions = mgr.get_user_permissions(identifier)

    # verify the table in table
    table = formatting.Table(['Name', 'Value'])
    permission_table = formatting.Table(['KeyName', 'Name'])
    for permission in all_permissions:
        if 'ALL_' in permission['key']:
            permission_table.add_row([permission.get('keyName'), permission.get('name')])

    hardwares = mgr.get_user_hardware(identifier)
    dedicatedhosts = mgr.get_user_dedicated_host(identifier)
    virtual_guests = mgr.get_user_virtuals(identifier)
    hardware_table = formatting.KeyValueTable(['Id', 'Device Name', 'Device type', 'Public Ip', 'Private Ip', 'notes'])
    virtual_table = formatting.KeyValueTable(['Id', 'Device Name', 'Device type', 'Public Ip', 'Private Ip', 'notes'])
    dedicated_table = formatting.KeyValueTable(['Id', 'Device Name', 'Device type', 'notes'])

    hardware_table.align['Device Name'] = 'l'
    dedicated_table.align['Device Name'] = 'l'
    virtual_table.align['Device Name'] = 'l'
    for hardware in hardwares:
        hardware_table.add_row([hardware.get('id'),
                                hardware.get('fullyQualifiedDomainName'),
                                'Bare Metal',
                                hardware.get('primaryIpAddress'),
                                hardware.get('primaryBackendIpAddress'),
                                hardware.get('notes') or '-'])
    for host in dedicatedhosts:
        dedicated_table.add_row([host.get('id'),
                                 host.get('name'),
                                 'Dedicated Host',
                                 host.get('notes') or '-'])
    for virtual in virtual_guests:
        virtual_table.add_row([virtual.get('id'),
                               virtual.get('fullyQualifiedDomainName'),
                               'virtual Guests',
                               virtual.get('primaryIpAddress'),
                               virtual.get('primaryBackendIpAddress'),
                               virtual.get('notes') or '-'])

    table.add_row(['Permission', permission_table])
    table.add_row(['Hardware', hardware_table])
    table.add_row(['Dedicated Host', dedicated_table])
    table.add_row(['Virtual Guest', virtual_table])

    env.fout(table)
