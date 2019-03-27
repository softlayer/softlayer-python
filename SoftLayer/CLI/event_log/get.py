"""Get Event Logs."""
# :license: MIT, see LICENSE for more details.

import json

import click

import SoftLayer
from SoftLayer import utils
from SoftLayer.CLI import environment

COLUMNS = ['event', 'object', 'type', 'date', 'username']


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
    """Get Event Logs"""

    event_mgr = SoftLayer.EventLogManager(env.client)
    user_mgr = SoftLayer.UserManager(env.client)
    request_filter = event_mgr.build_filter(date_min, date_max, obj_event, obj_id, obj_type, utc_offset)
    logs = event_mgr.get_event_logs(request_filter)
    log_time = "%Y-%m-%dT%H:%M:%S.%f%z"
    user_data = {}

    if metadata and 'metadata' not in COLUMNS:
        COLUMNS.append('metadata')

    row_count = 0
    for log, rows in logs:
        if log is None:
            click.secho('No logs available for filter %s.' % request_filter, fg='red')
            return

        if row_count == 0:
            if limit < 0:
                limit = rows
            click.secho("Number of records: %s" % rows, fg='red')
            click.secho(", ".join(COLUMNS))

        user = log['userType']
        label = log.get('label', '')
        if user == "CUSTOMER":
            username = user_data.get(log['userId'])
            if username is None:
                username = user_mgr.get_user(log['userId'], "mask[username]")['username']
                user_data[log['userId']] = username
            user = username

        if metadata:
            try:
                metadata_data = json.dumps(json.loads(log['metaData']), indent=4, sort_keys=True)
                if env.format == "table":
                    metadata_data = metadata_data.strip("{}\n\t")
            except ValueError:
                metadata_data = log['metaData']

            click.secho('"{0}","{1}","{2}","{3}","{4}","{5}"'.format(
                         log['eventName'],
                         label,
                         log['objectName'], 
                         utils.clean_time(log['eventCreateDate'], in_format=log_time), 
                         user, 
                         metadata_data)
            )
        else:
            click.secho('"{0}","{1}","{2}","{3}","{4}"'.format(
                         log['eventName'],
                         label,
                         log['objectName'], 
                         utils.clean_time(log['eventCreateDate'], in_format=log_time),
                         user)
            )

        row_count = row_count + 1
        if row_count >= limit:
            return

