# snapshot_enable.py
"""Create a file storage snapshot [ENABLE]."""

import click
import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions


@click.command()
@click.argument('volume_id')
@click.option('--schedule-type',
              help='Snapshot schedule [INTERVAL|HOURLY|DAILY|WEEKLY]',
              required=True)
@click.option('--retention-count',
              help='Number of snapshots to retain',
              required=True)
@click.option('--minute',
              help='Minute of the day when snapshots should be taken',
              default=0)
@click.option('--hour',
              help='Hour of the day when snapshots should be taken',
              default=0)
@click.option('--day-of-week',
              help='Day of the week when snapshots should be taken',
              default='SUNDAY')
@environment.pass_env
def cli(env, volume_id, schedule_type, retention_count,
        minute, hour, day_of_week):
    """Enables snapshots for a given volume on the specified schedule"""
    file_manager = SoftLayer.FileStorageManager(env.client)

    valid_schedule_types = {'INTERVAL', 'HOURLY', 'DAILY', 'WEEKLY'}
    valid_days = {'SUNDAY', 'MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY',
                  'FRIDAY', 'SATURDAY'}

    if schedule_type not in valid_schedule_types:
        raise exceptions.CLIAbort(
            '--schedule-type must be INTERVAL, HOURLY, ' +
            'DAILY, or WEEKLY, not ' + schedule_type)

    if schedule_type == 'INTERVAL' and (minute < 30 or minute > 59):
        raise exceptions.CLIAbort(
            '--minute value must be between 30 and 59')
    if minute < 0 or minute > 59:
        raise exceptions.CLIAbort(
            '--minute value must be between 0 and 59')
    if hour < 0 or hour > 23:
        raise exceptions.CLIAbort(
            '--hour value must be between 0 and 23')
    if day_of_week not in valid_days:
        raise exceptions.CLIAbort(
            '--day_of_week value must be a valid day (ex: SUNDAY)')

    enabled = file_manager.enable_snapshots(volume_id, schedule_type,
                                            retention_count, minute,
                                            hour, day_of_week)

    if enabled:
        click.echo('%s snapshots have been enabled for volume %s'
                   % (schedule_type, volume_id))
