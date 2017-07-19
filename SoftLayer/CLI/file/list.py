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
                         mask="fileNetworkMountAddress",),
    column_helper.Column('rep_partner_count', ('replicationPartnerCount',),
                         mask="replicationPartnerCount"),
    column_helper.Column(
        'created_by',
        ('billingItem', 'orderItem', 'order', 'userRecord', 'username')),
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
    'rep_partner_count'
]


@click.command()
@click.option('--username', '-u', help='Volume username')
@click.option('--datacenter', '-d', help='Datacenter shortname')
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
def cli(env, sortby, columns, datacenter, username, storage_type):
    """List file storage."""
    file_manager = SoftLayer.FileStorageManager(env.client)
    file_volumes = file_manager.list_file_volumes(datacenter=datacenter,
                                                  username=username,
                                                  storage_type=storage_type,
                                                  mask=columns.mask())

    table = formatting.Table(columns.columns)
    table.sortby = sortby

    for file_volume in file_volumes:
        table.add_row([value or formatting.blank()
                       for value in columns.row(file_volume)])

    env.fout(table)
