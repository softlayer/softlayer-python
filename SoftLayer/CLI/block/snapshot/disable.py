"""Disable scheduled snapshots of a specific volume"""
# :license: MIT, see LICENSE for more details.

import click
import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions


@click.command()
@click.argument('volume_id')
@click.option('--schedule-type',
              help='Snapshot schedule [HOURLY|DAILY|WEEKLY]',
              required=True)
@environment.pass_env
def cli(env, volume_id, schedule_type):
    """Disables snapshots on the specified schedule for a given volume"""

    if (schedule_type != 'HOURLY' and schedule_type != 'DAILY'
            and schedule_type != 'WEEKLY'):
        raise exceptions.CLIAbort(
            '--schedule-type must be HOURLY, DAILY, or WEEKLY')

    block_manager = SoftLayer.BlockStorageManager(env.client)
    disabled = block_manager.disable_snapshots(volume_id, schedule_type)

    if disabled:
        click.echo('%s snapshots have been disabled for volume %s'
                   % (schedule_type, volume_id))
