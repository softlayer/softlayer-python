"""Restore a file volume from a snapshot."""
# :license: MIT, see LICENSE for more details.

import click
import SoftLayer
from SoftLayer.CLI import environment


@click.command()
@click.argument('volume_id')
@click.option('--snapshot-id', '-s',
              help='The id of the snapshot which will be used'
              ' to restore the block volume')
@environment.pass_env
def cli(env, volume_id, snapshot_id):
    """Restore file volume using a given snapshot"""
    file_manager = SoftLayer.FileStorageManager(env.client)
    success = file_manager.restore_from_snapshot(volume_id, snapshot_id)

    if success:
        click.echo('File volume %s is being restored using snapshot %s'
                   % (volume_id, snapshot_id))
