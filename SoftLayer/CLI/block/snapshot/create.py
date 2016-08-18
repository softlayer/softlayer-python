"""Create a block storage snapshot."""
# :license: MIT, see LICENSE for more details.

import click
import SoftLayer
from SoftLayer.CLI import environment


@click.command()
@click.argument('volume_id')
@click.option('--notes', '-n',
              help='Notes to set on the new snapshot')
@environment.pass_env
def cli(env, volume_id, notes):
    """Creates a snapshot on a given volume"""
    block_manager = SoftLayer.BlockStorageManager(env.client)
    snapshot = block_manager.create_snapshot(volume_id, notes=notes)

    if 'id' in snapshot:
        click.echo('New snapshot created with id: %s' % snapshot['id'])
    else:
        click.echo('Error occurred while creating snapshot.\n'
                   'Ensure volume is not failed over or in another '
                   'state which prevents taking snapshots.')
