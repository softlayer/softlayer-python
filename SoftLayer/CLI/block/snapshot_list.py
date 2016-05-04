"""List block storage snapshots."""
# :license: MIT, see LICENSE for more details.

import click
import SoftLayer
from SoftLayer.CLI import columns as column_helper
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting


COLUMNS = [
    column_helper.Column(
        'id',
        ('snapshots', 'id',),
        mask='snapshots.id'),
    column_helper.Column('name', ('snapshots', 'notes',),
                         mask='snapshots.notes'),
    column_helper.Column('created',
                         ('snapshots', 'snapshotCreationTimestamp',),
                         mask='snapshots.snapshotCreationTimestamp'),
    column_helper.Column('size_bytes', ('snapshots', 'snapshotSizeBytes',),
                         mask='snapshots.snapshotSizeBytes'),
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
def cli(env, sortby, columns, volume_id):
    """List block storage snapshots."""
    block_manager = SoftLayer.BlockStorageManager(env.client)
    snapshots = block_manager.get_block_volume_snapshot_list(
        volume_id=volume_id,
        mask=columns.mask(),
    )

    table = formatting.Table(columns.columns)
    table.sortby = sortby

    for snapshot in snapshots:
        table.add_row([value or formatting.blank()
                       for value in columns.row(snapshot)])

    env.fout(table)
