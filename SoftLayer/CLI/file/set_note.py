"""Set note for an existing File storage volume."""
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
    """Set note for an existing file storage volume."""
    file_manager = SoftLayer.FileStorageManager(env.client)
    file_volume_id = helpers.resolve_id(file_manager.resolve_ids, volume_id, 'File Storage')

    result = file_manager.volume_set_note(file_volume_id, note)

    if result:
        click.echo("Set note successfully!")

    else:
        click.echo("Note could not be set! Please verify your options and try again.")
