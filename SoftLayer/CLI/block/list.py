"""List block storage volumes."""
# :license: MIT, see LICENSE for more details.

import SoftLayer
from SoftLayer.CLI import columns as column_helper
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting

import click

COLUMNS = [
    column_helper.Column('id', ('id',)),
    column_helper.Column('username', ('username',)),
    column_helper.Column('datacenter',
                         ('serviceResource', 'datacenter', 'name')),
    column_helper.Column('storageType', ('storageType', 'keyName')),
    column_helper.Column('capacityGb', ('capacityGb',)),
    column_helper.Column('bytesUsed', ('bytesUsed',)),
    column_helper.Column('ipAddr', ('serviceResourceBackendIpAddress',)),
]

DEFAULT_COLUMNS = [
    'id',
    'username',
    'datacenter',
    'storageType',
    'capacityGb',
    'bytesUsed',
    'ipAddr'
]


@click.command()
@click.option('--username', '-u', help='Volume username')
@click.option('--datacenter', '-d', help='Datacenter shortname')
@click.option('--storage_type',
              help='Type of storage volume',
              type=click.Choice(['performance', 'endurance']))
@click.option('--sortby', help='Column to sort by', default='username')
@click.option('--columns',
              callback=column_helper.get_formatter(COLUMNS),
              help='Columns to display. Options: {0}'.format(
                  ', '.join(column.name for column in COLUMNS)),
              default=','.join(DEFAULT_COLUMNS))
@environment.pass_env
def cli(env, sortby, columns, datacenter, username, storage_type):
    """List block storage."""
    block_manager = SoftLayer.BlockStorageManager(env.client)
    block_volumes = block_manager.list_block_volumes(datacenter=datacenter,
                                                     username=username,
                                                     storage_type=storage_type,
                                                     mask=columns.mask())

    table = formatting.Table(columns.columns)
    table.sortby = sortby

    for block_volume in block_volumes:
        block_volume['storageType']['keyName'] = block_volume['storageType'][
            'keyName'].split('_').pop(0)
        table.add_row([value or formatting.blank()
                       for value in columns.row(block_volume)])

    env.fout(table)
