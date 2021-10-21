"""Disable/Enable snapshots space usage threshold warning for a specific volume"""
# :license: MIT, see LICENSE for more details.

import click
import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions


@click.command()
@click.argument('volume_id')
@click.option(
    '--notification_flag',
    help=
    'Enable / disable sending sending notifications for snapshots space usage threshold warning [True|False]',
    required=True)
@environment.pass_env
def cli(env, volume_id, notification_flag):
    """Enables/Disables snapshot space usage threshold warning for a given volume"""

    if (notification_flag not in ['True', 'False']):
        raise exceptions.CLIAbort('--notification-flag must be True or False')

    file_manager = SoftLayer.FileStorageManager(env.client)
    disabled = file_manager.set_file_volume_snapshot_notification(
        volume_id, notification_flag)

    if disabled:
        click.echo(
            'Snapshots space usage threshold warning notification has bee set to %s for volume %s'
            % (notification - flag, volume_id))
