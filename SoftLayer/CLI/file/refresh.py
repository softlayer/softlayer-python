"""Refresh a dependent duplicate volume with a snapshot from its parent."""
# :license: MIT, see LICENSE for more details.

import click
import SoftLayer
from SoftLayer.CLI import environment


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.argument('volume_id')
@click.argument('snapshot_id')
@click.option('--force-refresh', '-f', is_flag=True, default=False, show_default=True,
              help="Cancel current refresh process and initiates the new refresh.")
@environment.pass_env
def cli(env, volume_id, snapshot_id, force_refresh):
    """Refresh a duplicate volume with a snapshot from its parent."""
    file_manager = SoftLayer.FileStorageManager(env.client)
    resp = file_manager.refresh_dupe(volume_id, snapshot_id, force_refresh)

    click.echo(resp)
