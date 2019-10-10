"""Retreive logs for an autoscale group"""
# :license: MIT, see LICENSE for more details.

import click

from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.managers.autoscale import AutoScaleManager
from SoftLayer import utils


@click.command()
@click.argument('identifier')
@click.option('--date-min', '-d', 'date_min', type=click.DateTime(formats=["%Y-%m-%d", "%m/%d/%Y"]),
              help='Earliest date to retreive logs for.')
@environment.pass_env
def cli(env, identifier, date_min):
    """Retreive logs for an autoscale group"""

    autoscale = AutoScaleManager(env.client)

    mask = "mask[id,createDate,description]"
    object_filter = {}
    if date_min:
        object_filter['logs'] = {
            'createDate': {
                'operation': 'greaterThanDate',
                'options': [{'name': 'date', 'value': [date_min.strftime("%m/%d/%Y")]}]
            }
        }

    logs = autoscale.get_logs(identifier, mask=mask, object_filter=object_filter)
    table = formatting.Table(['Date', 'Entry'], title="Logs")
    table.align['Entry'] = 'l'
    for log in logs:
        table.add_row([utils.clean_time(log.get('createDate')), log.get('description')])
    env.fout(table)
