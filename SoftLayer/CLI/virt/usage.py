"""Usage information of a virtual server."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers
from SoftLayer.utils import clean_time


@click.command()
@click.argument('identifier')
@click.option('--start_date', '-s', type=click.STRING, required=True, help="Start Date e.g. 2019-3-4 (yyyy-MM-dd)")
@click.option('--end_date', '-e', type=click.STRING, required=True, help="End Date e.g. 2019-4-2 (yyyy-MM-dd)")
@click.option('--valid_type', '-t', type=click.STRING, required=True,
              help="Metric_Data_Type keyName e.g. CPU0, CPU1, MEMORY_USAGE, etc.")
@click.option('--summary_period', '-p', type=click.INT, default=3600,
              help="300, 600, 1800, 3600, 43200 or 86400 seconds")
@environment.pass_env
def cli(env, identifier, start_date, end_date, valid_type, summary_period):
    """Usage information of a virtual server."""

    vsi = SoftLayer.VSManager(env.client)
    table = formatting.Table(['counter', 'dateTime', 'type'])
    table_average = formatting.Table(['Average'])

    vs_id = helpers.resolve_id(vsi.resolve_ids, identifier, 'VS')

    result = vsi.get_summary_data_usage(vs_id, start_date=start_date, end_date=end_date,
                                        valid_type=valid_type, summary_period=summary_period)

    if len(result) == 0:
        raise exceptions.CLIAbort('No metric data for this range of dates provided')

    count = 0
    counter = 0.00
    for data in result:
        if valid_type == "MEMORY_USAGE":
            usage_counter = data['counter'] / 2 ** 30
        else:
            usage_counter = data['counter']

        table.add_row([
            round(usage_counter, 2),
            clean_time(data['dateTime']),
            data['type'],
        ])
        counter = counter + usage_counter
        count = count + 1

    average = counter / count

    env.fout(table_average.add_row([round(average, 2)]))

    env.fout(table_average)
    env.fout(table)
