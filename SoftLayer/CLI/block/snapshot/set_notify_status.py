"""Disable/Enable snapshots space usage threshold warning for a specific volume"""
# :license: MIT, see LICENSE for more details.

import click
import SoftLayer
from SoftLayer.CLI import environment


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.argument('volume_id')
@click.option(
    '--enable/--disable',
    default=True,
    help="""
    Enable/Disable snapshot notification. Use `slcli block snapshot-set-notification volumeId --enable` to enable.
    """,
    required=True)
@environment.pass_env
def cli(env, volume_id, enable):
    """Enables/Disables snapshot space usage threshold warning for a given volume."""
    block_manager = SoftLayer.BlockStorageManager(env.client)

    status = block_manager.set_volume_snapshot_notification(volume_id, enable)

    if status:
        click.echo(
            'Snapshots space usage threshold warning notification has bee set to %s for volume %s'
            % (enable, volume_id))
