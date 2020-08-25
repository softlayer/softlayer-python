"""Set note for an existing block storage volume."""
# :license: MIT, see LICENSE for more details.

import click
import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import helpers


@click.command()
@click.argument('volume-id')
@click.option('--note', '-n',
              type=str,
              required=True,
              help='Public notes related to a Storage volume')
@environment.pass_env
def cli(env, volume_id, note):
    """Set note for an existing block storage volume."""
    block_manager = SoftLayer.BlockStorageManager(env.client)
    block_volume_id = helpers.resolve_id(block_manager.resolve_ids, volume_id, 'Block Volume')

    result = block_manager.volume_set_note(block_volume_id, note)

    if result:
        click.echo("Set note successfully!")

    else:
        click.echo("Note could not be set! Please verify your options and try again.")
