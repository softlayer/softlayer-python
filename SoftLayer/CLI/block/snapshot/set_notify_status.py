"""Disable/Enable snapshots space usage threshold warning for a specific volume"""
# :license: MIT, see LICENSE for more details.

import click
import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions


@click.command()
@click.argument('volume_id')
@click.option('--enable/--disable', default=True,
    help=
    'Enable/Disable snapshot usage warning notification. Use  `slcli block snapshot-set-notification volumeId --enable` to enable',
    required=True)
@environment.pass_env
def cli(env, volume_id, enable):
    """Enables/Disables snapshot space usage threshold warning for a given volume"""
    block_manager = SoftLayer.BlockStorageManager(env.client)

    if enable:
        enabled = 'True'
    else:
        enabled = 'False'
    status = block_manager.set_block_volume_snapshot_notification(
        volume_id, enabled)

    if status:
        click.echo(
            'Snapshots space usage threshold warning notification has bee set to %s for volume %s'
            % (enabled, volume_id))
