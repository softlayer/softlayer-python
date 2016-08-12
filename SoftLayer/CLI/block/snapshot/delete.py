"""Delete a block storage snapshot."""
# :license: MIT, see LICENSE for more details.

import click
import SoftLayer
from SoftLayer.CLI import environment


@click.command()
@click.argument('snapshot_id')
@environment.pass_env
def cli(env, snapshot_id):
    """Deletes a snapshot on a given volume"""
    block_manager = SoftLayer.BlockStorageManager(env.client)
    deleted = block_manager.delete_snapshot(snapshot_id)

    if deleted:
        click.echo('Snapshot %s deleted' % snapshot_id)
