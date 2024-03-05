"""Get the snapshots space usage threshold warning flag setting for specific volume"""
# :license: MIT, see LICENSE for more details.

import click
import SoftLayer
from SoftLayer.CLI import environment


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.argument('volume_id')
@environment.pass_env
def cli(env, volume_id):
    """Get snapshots space usage threshold warning flag setting for a given volume."""
    block_manager = SoftLayer.BlockStorageManager(env.client)
    enabled = block_manager.get_volume_snapshot_notification_status(volume_id)

    if enabled == 0:
        click.echo(f"Disabled: Snapshots space usage threshold is disabled for volume {volume_id}")
    else:
        click.echo(f"Enabled: Snapshots space usage threshold is enabled for volume {volume_id}")
