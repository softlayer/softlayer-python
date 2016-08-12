"""List block storage snapshots."""
# :license: MIT, see LICENSE for more details.

import click
import SoftLayer
from SoftLayer.CLI import columns as column_helper
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting


COLUMNS = [
    column_helper.Column('id', ('id',), mask='id'),
    column_helper.Column('name', ('notes',), mask='notes'),
    column_helper.Column('created', ('snapshotCreationTimestamp',),
                         mask='snapshotCreationTimestamp'),
    column_helper.Column('size_bytes', ('snapshotSizeBytes',),
                         mask='snapshotSizeBytes'),
]

DEFAULT_COLUMNS = [
    'id',
    'name',
    'created',
    'size_bytes'
]


@click.command()
@click.argument('volume_id')
@click.option('--sortby', help='Column to sort by',
              default='created')
@click.option('--columns',
              callback=column_helper.get_formatter(COLUMNS),
              help='Columns to display. Options: {0}'.format(
                  ', '.join(column.name for column in COLUMNS)),
              default=','.join(DEFAULT_COLUMNS))
@environment.pass_env
def cli(env, volume_id, sortby, columns):
    """List block storage snapshots."""
    block_manager = SoftLayer.BlockStorageManager(env.client)
    snapshots = block_manager.get_block_volume_snapshot_list(
        volume_id,
        mask=columns.mask()
    )

    table = formatting.Table(columns.columns)
    table.sortby = sortby

    for snapshot in snapshots:
        table.add_row([value or formatting.blank()
                       for value in columns.row(snapshot)])

    env.fout(table)
