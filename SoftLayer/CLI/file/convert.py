"""Convert a dependent duplicate volume to an independent volume."""
# :license: MIT, see LICENSE for more details.

import click
import SoftLayer
from SoftLayer.CLI import environment


@click.command()
@click.argument('volume_id')
@environment.pass_env
def cli(env, volume_id):
    """Convert a dependent duplicate volume to an independent volume."""
    file_manager = SoftLayer.FileStorageManager(env.client)
    resp = file_manager.convert_dep_dupe(volume_id)

    click.echo(resp)
