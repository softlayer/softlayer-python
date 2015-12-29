"""List block storage snapshots."""
# :license: MIT, see LICENSE for more details.

import click
import SoftLayer
from SoftLayer.CLI import columns as column_helper
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting


COLUMNS = [
    column_helper.Column('id', ('id',)),
    column_helper.Column('name', ('name',)),
    column_helper.Column('snapshotCreationTimestamp',
                         ('snapshotCreationTimestamp',)),
    column_helper.Column('snapshotSizeBytes', ('snapshotSizeBytes',)),
]

DEFAULT_COLUMNS = [
    'id',
    'name',
    'snapshotCreationTimestamp',
    'snapshotSizeBytes'
]


@click.command()
@click.argument('volume_id')
@click.option('--sortby', help='Column to sort by',
              default='snapshotCreationTimestamp')
@click.option('--columns',
              callback=column_helper.get_formatter(COLUMNS),
              help='Columns to display. Options: {0}'.format(
                  ', '.join(column.name for column in COLUMNS)),
              default=','.join(DEFAULT_COLUMNS))
@environment.pass_env
def cli(env, sortby, columns, volume_id):
    """List block storage."""
    block_manager = SoftLayer.BlockStorageManager(env.client)
    volume = block_manager.get_block_volume_snapshot_list(volume_id=volume_id)

    table = formatting.Table(columns.columns)
    table.sortby = sortby

    if volume and 'snapshots' in volume.keys():
        for snapshot in volume['snapshots']:

            if 'notes' in snapshot.keys():
                snapshot['name'] = snapshot['notes']

            table.add_row([value or formatting.blank()
                           for value in columns.row(snapshot)])

        env.fout(table)
    else:
        click.echo("No snapshots found.")
