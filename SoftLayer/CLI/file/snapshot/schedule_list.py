"""List scheduled snapshots of a specific volume"""
# :license: MIT, see LICENSE for more details.

import click
import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting


@click.command()
@click.argument('volume_id')
@environment.pass_env
def cli(env, volume_id):
    """Lists snapshot schedules for a given volume"""

    file_manager = SoftLayer.FileStorageManager(env.client)

    snapshot_schedules = file_manager.list_volume_schedules(volume_id)

    table = formatting.Table(['id',
                              'active',
                              'type',
                              'replication',
                              'date_created',
                              'minute',
                              'hour',
                              'day',
                              'week',
                              'day_of_week',
                              'date_of_month',
                              'month_of_year',
                              'maximum_snapshots'])

    for schedule in snapshot_schedules:

        if 'REPLICATION' in schedule['type']['keyname']:
            replication = '*'
        else:
            replication = formatting.blank()

        file_schedule_type = schedule['type']['keyname'].replace('REPLICATION_', '')
        file_schedule_type = file_schedule_type.replace('SNAPSHOT_', '')

        property_list = ['MINUTE', 'HOUR', 'DAY', 'WEEK',
                         'DAY_OF_WEEK', 'DAY_OF_MONTH',
                         'MONTH_OF_YEAR', 'SNAPSHOT_LIMIT']

        schedule_properties = []
        for prop_key in property_list:
            item = formatting.blank()
            for schedule_property in schedule.get('properties', []):
                if schedule_property['type']['keyname'] == prop_key:
                    if schedule_property['value'] == '-1':
                        item = '*'
                    else:
                        item = schedule_property['value']
                    break
            schedule_properties.append(item)

        table_row = [
            schedule['id'],
            '*' if schedule.get('active', '') else '',
            file_schedule_type,
            replication,
            schedule.get('createDate', '')
        ]
        table_row.extend(schedule_properties)
        table.add_row(table_row)

    env.fout(table)
