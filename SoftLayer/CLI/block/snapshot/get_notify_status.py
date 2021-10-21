"""Get the snapshots space usage threshold warning flag setting for specific volume"""
# :license: MIT, see LICENSE for more details.

import click
import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions


@click.command()
@click.argument('volume_id')
@environment.pass_env
def cli(env, volume_id):
    """Get snapshots space usage threshold warning flag setting for a given volume"""

    block_manager = SoftLayer.BlockStorageManager(env.client)
    enabled = block_manager.get_block_snapshots_notification_status(volume_id)

    if (enabled == ''):
        click.echo(
            'Snapshots space usage threshold warning flag setting is null. Set to default value enable. For volume %s'
            % (volume_id))
    elif (enabled == 'True'):
        click.echo(
            'Snapshots space usage threshold warning flag setting is enabled for volume %s'
            % (volume_id))
    else:
        click.echo(
            'Snapshots space usage threshold warning flag setting is disabled for volume %s'
            % (volume_id))
