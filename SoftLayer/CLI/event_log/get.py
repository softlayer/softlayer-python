"""Get Event Logs."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer import utils


@click.command()
@click.option('--date-min', '-d',
              help='The earliest date we want to search for event logs in mm/dd/yyyy format.')
@click.option('--date-max', '-D',
              help='The latest date we want to search for event logs in mm/dd/yyyy format.')
@click.option('--obj-event', '-e',
              help="The event we want to get event logs for")
@click.option('--obj-id', '-i',
              help="The id of the object we want to get event logs for")
@click.option('--obj-type', '-t',
              help="The type of the object we want to get event logs for")
@click.option('--utc-offset', '-z', default='-0000', show_default=True,
              help="UTC Offset for searching with dates. +/-HHMM format")
@click.option('--metadata/--no-metadata', default=False, show_default=True,
              help="Display metadata if present")
@click.option('--limit', '-l', type=click.INT, default=50, show_default=True,
              help="Total number of result to return. -1 to return ALL, there may be a LOT of these.")
@environment.pass_env
def cli(env, date_min, date_max, obj_event, obj_id, obj_type, utc_offset, metadata, limit):
    """Get Event Logs

    Example:
        slcli event-log get -d 01/01/2019 -D 02/01/2019 -t User -l 10
    """
    columns = ['Event', 'Object', 'Type', 'Date', 'Username']

    event_mgr = SoftLayer.EventLogManager(env.client)
    user_mgr = SoftLayer.UserManager(env.client)
    request_filter = event_mgr.build_filter(date_min, date_max, obj_event, obj_id, obj_type, utc_offset)
    logs = event_mgr.get_event_logs(request_filter)
    log_time = "%Y-%m-%dT%H:%M:%S.%f%z"
    user_data = {}

    if metadata:
        columns.append('Metadata')

    row_count = 0
    click.secho(", ".join(columns))
    for log in logs:
        if log is None:
            click.secho('No logs available for filter %s.' % request_filter, fg='red')
            return

        user = log['userType']
        label = log.get('label', '')
        if user == "CUSTOMER":
            username = user_data.get(log['userId'])
            if username is None:
                username = user_mgr.get_user(log['userId'], "mask[username]")['username']
                user_data[log['userId']] = username
            user = username

        if metadata:
            metadata_data = log['metaData'].strip("\n\t")

            click.secho("'{0}','{1}','{2}','{3}','{4}','{5}'".format(
                log['eventName'],
                label,
                log['objectName'],
                utils.clean_time(log['eventCreateDate'], in_format=log_time),
                user,
                metadata_data))
        else:
            click.secho("'{0}','{1}','{2}','{3}','{4}'".format(
                log['eventName'],
                label,
                log['objectName'],
                utils.clean_time(log['eventCreateDate'], in_format=log_time),
                user))

        row_count = row_count + 1
        if row_count >= limit and limit != -1:
            return
