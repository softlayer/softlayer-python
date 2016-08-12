"""Restore a block volume from a snapshot."""
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
    """Restore block volume using a given snapshot"""
    block_manager = SoftLayer.BlockStorageManager(env.client)
    success = block_manager.restore_from_snapshot(volume_id, snapshot_id)

    if success:
        click.echo('Block volume %s is being restored using snapshot %s'
                   % (volume_id, snapshot_id))
