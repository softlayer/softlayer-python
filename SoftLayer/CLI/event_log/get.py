"""Get Event Logs."""
# :license: MIT, see LICENSE for more details.

import click
import json

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
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
    mgr = SoftLayer.NetworkManager(env.client)

    filter = _build_filter(obj_id, obj_type)

    logs = mgr.get_event_logs(filter)

    table = formatting.Table(COLUMNS)
    table.align['metadata'] = "l"

    for log in logs:
        metadata = json.loads(log['metaData'])

        table.add_row([log['eventName'], log['label'], log['eventCreateDate'], json.dumps(metadata, indent=4, sort_keys=True)])

    env.fout(table)


def _build_filter(obj_id, obj_type):
    if not obj_id and not obj_type:
        return None
    
    filter = {}

    if obj_id:
        filter['objectId'] = {'operation': obj_id}

    if obj_type:
        filter['objectName'] = {'operation': obj_type}

    return filter
