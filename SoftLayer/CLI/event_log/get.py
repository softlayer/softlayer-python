"""Get Audit Logs."""
# :license: MIT, see LICENSE for more details.

from datetime import datetime
import json

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting

COLUMNS = ['event', 'label', 'date', 'metadata']


@click.command()
@click.option('--date_min', '-d',
              help='The earliest date we want to search for audit logs in mm/dd/yyy format.')
@click.option('--date_max', '-D',
              help='The latest date we want to search for audit logs in mm/dd/yyy format.')
@click.option('--obj_event', '-e',
              help="The event we want to get audit logs for")
@click.option('--obj_id', '-i',
              help="The id of the object we want to get audit logs for")
@click.option('--request_id', '-r',
              help="The request id we want to look for. If this is set, we will ignore all other arguments.")
@click.option('--obj_type', '-t',
              help="The type of the object we want to get audit logs for")
@click.option('--utc_offset', '-z',
              help="UTC Offset for seatching with dates. The default is -0500")
@environment.pass_env
def cli(env, date_min, date_max, obj_event, obj_id, request_id, obj_type, utc_offset):
    """Get Audit Logs"""
    mgr = SoftLayer.EventLogManager(env.client)

    if request_id is not None:
        logs = _get_event_logs_by_request_id(mgr, request_id)
    else:
        request_filter = _build_filter(date_min, date_max, obj_event, obj_id, obj_type, utc_offset)
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


def _build_filter(date_min, date_max, obj_event, obj_id, obj_type, utc_offset):
    if not date_min and not date_max and not obj_event and not obj_id and not obj_type:
        return None

    request_filter = {}

    if date_min and date_max:
        request_filter['eventCreateDate'] = {
            'operation': 'betweenDate',
            'options': [
                {
                    'name': 'startDate',
                    'value': [_parse_date(date_min, utc_offset)]
                },
                {
                    'name': 'endDate',
                    'value': [_parse_date(date_max, utc_offset)]
                }
            ]
        }

    else:
        if date_min:
            request_filter['eventCreateDate'] = {
                'operation': 'greaterThanDate',
                'options': [
                    {
                        'name': 'date',
                        'value': [_parse_date(date_min, utc_offset)]
                    }
                ]
            }

        if date_max:
            request_filter['eventCreateDate'] = {
                'operation': 'lessThanDate',
                'options': [
                    {
                        'name': 'date',
                        'value': [_parse_date(date_max, utc_offset)]
                    }
                ]
            }

    if obj_event:
        request_filter['eventName'] = {'operation': obj_event}

    if obj_id:
        request_filter['objectId'] = {'operation': obj_id}

    if obj_type:
        request_filter['objectName'] = {'operation': obj_type}

    return request_filter


def _get_event_logs_by_request_id(mgr, request_id):
    cci_filter = {
        'objectName': {
            'operation': 'CCI'
        }
    }

    cci_logs = mgr.get_event_logs(cci_filter)

    security_group_filter = {
        'objectName': {
            'operation': 'Security Group'
        }
    }

    security_group_logs = mgr.get_event_logs(security_group_filter)

    unfiltered_logs = cci_logs + security_group_logs

    filtered_logs = []

    for unfiltered_log in unfiltered_logs:
        try:
            metadata = json.loads(unfiltered_log['metaData'])
            if 'requestId' in metadata:
                if metadata['requestId'] == request_id:
                    filtered_logs.append(unfiltered_log)
        except ValueError:
            continue

    return filtered_logs


def _parse_date(date_string, utc_offset):
    user_date_format = "%m/%d/%Y"

    user_date = datetime.strptime(date_string, user_date_format)
    dirty_time = user_date.isoformat()

    if utc_offset is None:
        utc_offset = "-0500"

    iso_time_zone = utc_offset[:3] + ':' + utc_offset[3:]
    clean_time = "{}.000000{}".format(dirty_time, iso_time_zone)

    return clean_time
