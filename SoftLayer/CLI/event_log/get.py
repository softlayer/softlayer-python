"""Get Event Logs."""
# :license: MIT, see LICENSE for more details.

import json
import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting

COLUMNS = ['event', 'label', 'date', 'metadata']


@click.command()
@click.option('--obj_id', '-i',
              help="The id of the object we want to get event logs for")
@click.option('--obj_type', '-t',
              help="The type of the object we want to get event logs for")
@environment.pass_env
def cli(env, obj_id, obj_type):
    """Get Event Logs"""
    mgr = SoftLayer.EventLogManager(env.client)

    request_filter = _build_filter(obj_id, obj_type)

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


def _build_filter(obj_id, obj_type):
    if not obj_id and not obj_type:
        return None

    request_filter = {}

    if obj_id:
        request_filter['objectId'] = {'operation': obj_id}

    if obj_type:
        request_filter['objectName'] = {'operation': obj_type}

    return request_filter
