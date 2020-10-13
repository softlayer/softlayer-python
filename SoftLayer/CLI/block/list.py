"""List block storage volumes."""
# :license: MIT, see LICENSE for more details.

import click
import SoftLayer
from SoftLayer.CLI import columns as column_helper
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting


COLUMNS = [
    column_helper.Column('id', ('id',), mask="id"),
    column_helper.Column('username', ('username',), mask="username"),
    column_helper.Column('datacenter',
                         ('serviceResource', 'datacenter', 'name'),
                         mask="serviceResource.datacenter.name"),
    column_helper.Column(
        'storage_type',
        lambda b: b['storageType']['keyName'].split('_').pop(0)
        if 'storageType' in b and 'keyName' in b['storageType']
        and isinstance(b['storageType']['keyName'], str)
        else '-',
        mask="storageType.keyName"),
    column_helper.Column('capacity_gb', ('capacityGb',), mask="capacityGb"),
    column_helper.Column('bytes_used', ('bytesUsed',), mask="bytesUsed"),
    column_helper.Column('iops', ('iops',), mask="iops"),
    column_helper.Column('ip_addr', ('serviceResourceBackendIpAddress',),
                         mask="serviceResourceBackendIpAddress"),
    column_helper.Column('lunId', ('lunId',), mask="lunId"),
    column_helper.Column('active_transactions', ('activeTransactionCount',),
                         mask="activeTransactionCount"),
    column_helper.Column('rep_partner_count', ('replicationPartnerCount',),
                         mask="replicationPartnerCount"),
    column_helper.Column(
        'created_by',
        ('billingItem', 'orderItem', 'order', 'userRecord', 'username')),
    column_helper.Column('notes', ('notes',), mask="notes"),
]

DEFAULT_COLUMNS = [
    'id',
    'username',
    'datacenter',
    'storage_type',
    'capacity_gb',
    'bytes_used',
    'iops',
    'ip_addr',
    'lunId',
    'active_transactions',
    'rep_partner_count',
    'notes'
]

DEFAULT_NOTES_SIZE = 20


@click.command()
@click.option('--username', '-u', help='Volume username')
@click.option('--datacenter', '-d', help='Datacenter shortname')
@click.option('--order', '-o', type=int, help='Filter by ID of the order that purchased the block storage')
@click.option('--storage-type',
              help='Type of storage volume',
              type=click.Choice(['performance', 'endurance']))
@click.option('--sortby', help='Column to sort by', default='username')
@click.option('--columns',
              callback=column_helper.get_formatter(COLUMNS),
              help='Columns to display. Options: {0}'.format(
                  ', '.join(column.name for column in COLUMNS)),
              default=','.join(DEFAULT_COLUMNS))
@environment.pass_env
def cli(env, sortby, columns, datacenter, username, storage_type, order):
    """List block storage."""
    block_manager = SoftLayer.BlockStorageManager(env.client)
    block_volumes = block_manager.list_block_volumes(datacenter=datacenter,
                                                     username=username,
                                                     storage_type=storage_type,
                                                     order=order,
                                                     mask=columns.mask())

    table = formatting.Table(columns.columns)
    table.sortby = sortby

    _reduce_notes(block_volumes)

    for block_volume in block_volumes:
        table.add_row([value or formatting.blank()
                       for value in columns.row(block_volume)])

    env.fout(table)


def _reduce_notes(block_volumes):
    """Reduces the size of the notes in a volume list.

    :param block_volumes: An list of block volumes
    """
    for block_volume in block_volumes:
        if len(block_volume.get('notes', '')) > DEFAULT_NOTES_SIZE:
            shortened_notes = block_volume['notes'][:DEFAULT_NOTES_SIZE]
            block_volume['notes'] = shortened_notes
