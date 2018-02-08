"""Get event logs relating to security groups"""
# :license: MIT, see LICENSE for more details.

import json

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting

COLUMNS = ['event', 'label', 'date', 'metadata']


@click.command()
@click.argument('request_id')
@environment.pass_env
def get_by_request_id(env, request_id):
    """Search for event logs by request id"""
    mgr = SoftLayer.NetworkManager(env.client)

    logs = mgr.get_event_logs_by_request_id(request_id)

    table = formatting.Table(COLUMNS)
    table.align['metadata'] = "l"

    for log in logs:
        metadata = json.dumps(json.loads(log['metaData']), indent=4, sort_keys=True)

        table.add_row([log['eventName'], log['label'], log['eventCreateDate'], metadata])

    env.fout(table)
