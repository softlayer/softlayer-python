"""Refresh a dependent duplicate volume with a snapshot from its parent."""
# :license: MIT, see LICENSE for more details.

import click
import SoftLayer
from SoftLayer.CLI import environment


@click.command()
@click.argument('volume_id')
@click.argument('snapshot_id')
@environment.pass_env
def cli(env, volume_id, snapshot_id):
    """Refresh a duplicate volume with a snapshot from its parent."""
    file_manager = SoftLayer.FileStorageManager(env.client)
    resp = file_manager.refresh_dupe(volume_id, snapshot_id)

    click.echo(resp)
