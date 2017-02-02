"""List hosts with access to file volume."""
# :license: MIT, see LICENSE for more details.

import click
import SoftLayer
from SoftLayer.CLI import columns as column_helper
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.CLI import storage_utils


@click.command()
@click.argument('volume_id')
@click.option('--sortby', help='Column to sort by', default='name')
@click.option('--columns',
              callback=column_helper.get_formatter(storage_utils.COLUMNS),
              help='Columns to display. Options: {0}'.format(
                  ', '.join(column.name for column in storage_utils.COLUMNS)),
              default=','.join(storage_utils.DEFAULT_COLUMNS))
@environment.pass_env
def cli(env, columns, sortby, volume_id):
    """List ACLs."""
    file_manager = SoftLayer.FileStorageManager(env.client)
    access_list = file_manager.get_file_volume_access_list(
        volume_id=volume_id)
    table = formatting.Table(columns.columns)
    table.sortby = sortby

    for key, type_name in [('allowedVirtualGuests', 'VIRTUAL'),
                           ('allowedHardware', 'HARDWARE'),
                           ('allowedSubnets', 'SUBNET'),
                           ('allowedIpAddresses', 'IP')]:
        for obj in access_list.get(key, []):
            obj['type'] = type_name
            table.add_row([value or formatting.blank()
                           for value in columns.row(obj)])

    env.fout(table)
