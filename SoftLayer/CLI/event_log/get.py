"""Get Event Logs."""
# :license: MIT, see LICENSE for more details.

import json

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting

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
@click.option('--utc-offset', '-z',
              help="UTC Offset for searching with dates. The default is -0000")
@click.option('--metadata/--no-metadata', default=False,
              help="Display metadata if present")
@environment.pass_env
def cli(env, date_min, date_max, obj_event, obj_id, obj_type, utc_offset, metadata):
    """Get Event Logs"""
    mgr = SoftLayer.EventLogManager(env.client)
    usrmgr = SoftLayer.UserManager(env.client)
    request_filter = mgr.build_filter(date_min, date_max, obj_event, obj_id, obj_type, utc_offset)
    logs = mgr.get_event_logs(request_filter)

    if logs is None:
        env.fout('None available.')
        return

    if metadata and 'metadata' not in COLUMNS:
        COLUMNS.append('metadata')

    table = formatting.Table(COLUMNS)
    if metadata:
        table.align['metadata'] = "l"

    for log in logs:
        user = log['userType']
        if user == "CUSTOMER":
            user = usrmgr.get_user(log['userId'], "mask[username]")['username']
        if metadata:
            try:
                metadata_data = json.dumps(json.loads(log['metaData']), indent=4, sort_keys=True)
                if env.format == "table":
                    metadata_data = metadata_data.strip("{}\n\t")
            except ValueError:
                metadata_data = log['metaData']

            table.add_row([log['eventName'], log['label'], log['objectName'],
                           log['eventCreateDate'], user, metadata_data])
        else:
            table.add_row([log['eventName'], log['label'], log['objectName'],
                           log['eventCreateDate'], user])
    env.fout(table)
