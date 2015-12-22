"""List hosts with access to volume."""
# :license: MIT, see LICENSE for more details.

import click
import SoftLayer
from SoftLayer.CLI import columns as column_helper
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting


COLUMNS = [
    column_helper.Column(
        'id',
        ('id',)),
    column_helper.Column(
        'hostname',
        ('hostname',)),
    column_helper.Column(
        'type',
        ('type',)),
    column_helper.Column(
        'primaryBackendIpAddress',
        ('primaryBackendIpAddress',)),
    column_helper.Column(
        'hostIqn',
        ('allowedHost', 'name',)),
    column_helper.Column(
        'username',
        ('allowedHost', 'credential', 'username',)),
    column_helper.Column(
        'password',
        ('allowedHost', 'credential', 'password',)),
]

DEFAULT_COLUMNS = [
    'id',
    'hostname',
    'type',
    'primaryBackendIpAddress',
    'hostIqn',
    'username',
    'password',
]


@click.command()
@click.argument('volume_id')
@click.option('--sortby', help='Column to sort by', default='hostname')
@click.option('--columns',
              callback=column_helper.get_formatter(COLUMNS),
              help='Columns to display. Options: {0}'.format(
                  ', '.join(column.name for column in COLUMNS)),
              default=','.join(DEFAULT_COLUMNS))
@environment.pass_env
def cli(env, columns, sortby, volume_id):
    """List block storage."""
    block_manager = SoftLayer.BlockStorageManager(env.client)
    access_list = block_manager.get_block_volume_access_list(
        volume_id=volume_id)
    table = formatting.Table(columns.columns)
    table.sortby = sortby

    if access_list:
        if 'allowedVirtualGuests' in access_list.keys():
            for host in access_list['allowedVirtualGuests']:
                host['type'] = 'VIRTUAL'
                host['hostname'] = "{0}.{1}".format(
                    host['hostname'],
                    host['domain'])
                table.add_row([value or formatting.blank()
                               for value in columns.row(host)])

        if 'allowedHardware' in access_list.keys():
            for host in access_list['allowedHardware']:
                host['type'] = 'HARDWARE'
                host['hostname'] = "{0}.{1}".format(
                    host['hostname'],
                    host['domain'])
                table.add_row([value or formatting.blank()
                               for value in columns.row(host)])

        if 'allowedSubnets' in access_list.keys():
            for host in access_list['allowedSubnets']:
                host['type'] = 'SUBNET'
                if 'note' in host.keys():
                    host['hostname'] = "{0}/{1} ({3})".format(
                        host['networkIdentifier'],
                        host['cidr'],
                        host['note'],
                    )
                else:
                    host['hostname'] = "{0}/{1}".format(
                        host['networkIdentifier'],
                        host['cidr']
                    )
                table.add_row([value or formatting.blank()
                               for value in columns.row(host)])

        if 'allowedIpAddresses' in access_list.keys():
            for host in access_list['allowedIpAddresses']:
                host['type'] = 'IP'
                if 'note' in host.keys():
                    host['hostname'] = "{0} ({1})".format(
                        host['ipAddress'],
                        host['note']
                    )
                else:
                    host['hostname'] = host['ipAddress']
                table.add_row([value or formatting.blank()
                               for value in columns.row(host)])

        env.fout(table)
    else:
        click.echo("No authorized hosts found.")
