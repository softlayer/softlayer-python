"""Get Event Logs."""
# :license: MIT, see LICENSE for more details.

import json

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting

COLUMNS = ['event', 'label', 'date', 'metadata']


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
@environment.pass_env
def cli(env, date_min, date_max, obj_event, obj_id, obj_type, utc_offset):
    """Get Event Logs"""
    mgr = SoftLayer.EventLogManager(env.client)

    request_filter = mgr.build_filter(date_min, date_max, obj_event, obj_id, obj_type, utc_offset)
    logs = mgr.get_event_logs(request_filter)

    table = formatting.Table(COLUMNS)
    table.align['metadata'] = "l"

    for log in logs:
        try:
            metadata = json.dumps(json.loads(log['metaData']), indent=4, sort_keys=True)
        except ValueError:
            metadata = log['metaData']

        table.add_row([log['eventName'], log['label'], log['eventCreateDate'], metadata])

    env.fout(table)
