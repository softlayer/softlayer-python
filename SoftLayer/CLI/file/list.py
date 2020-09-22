"""List file storage volumes."""
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
    column_helper.Column('ip_addr', ('serviceResourceBackendIpAddress',),
                         mask="serviceResourceBackendIpAddress"),
    column_helper.Column('active_transactions', ('activeTransactionCount',),
                         mask="activeTransactionCount"),
    column_helper.Column('mount_addr', ('fileNetworkMountAddress',),
                         mask="fileNetworkMountAddress", ),
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
    'ip_addr',
    'active_transactions',
    'mount_addr',
    'rep_partner_count',
    'notes',
]

DEFAULT_NOTES_SIZE = 20


@click.command()
@click.option('--username', '-u', help='Volume username')
@click.option('--datacenter', '-d', help='Datacenter shortname')
@click.option('--order', '-o', help='Filter by ID of the order that purchased the block storage')
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
def cli(env, sortby, columns, datacenter, username, order, storage_type):
    """List file storage."""
    file_manager = SoftLayer.FileStorageManager(env.client)
    file_volumes = file_manager.list_file_volumes(datacenter=datacenter,
                                                  username=username,
                                                  order=order,
                                                  storage_type=storage_type,
                                                  mask=columns.mask())

    table = formatting.Table(columns.columns)
    table.sortby = sortby

    _reduce_notes(file_volumes)

    for file_volume in file_volumes:
        table.add_row([value or formatting.blank()
                       for value in columns.row(file_volume)])

    env.fout(table)


def _reduce_notes(file_volumes):
    """Reduces the size of the notes in a volume list.

    :param file_volumes: An list of file volumes
    """
    for file_volume in file_volumes:
        if len(file_volume.get('notes', '')) > DEFAULT_NOTES_SIZE:
            shortened_notes = file_volume['notes'][:DEFAULT_NOTES_SIZE]
            file_volume['notes'] = shortened_notes
