"""Usage information of a virtual server."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment, helpers
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting


@click.command(short_help="Usage information of a virtual server.")
@click.argument('identifier')
@click.option('--start_date', '-s', type=click.STRING, required=True, help="Start Date e.g. 2019-3-4")
@click.option('--end_date', '-e', type=click.STRING, required=True, help="End Date e.g. 2019-4-2")
@click.option('--valid_type', '-t', type=click.STRING, required=True,
              help="Metric_Data_Type keyName e.g. CPU0, CPU1, MEMORY_USAGE, etc.")
@click.option('--summary_period', '-summary', type=click.INT, required=True,
              help="300, 600, 1800, 3600, 43200 or 86400 seconds")
@environment.pass_env
def cli(env, identifier, start_date, end_date, valid_type, summary_period):
    """Usage information of a virtual server."""

    vsi = SoftLayer.VSManager(env.client)
    table = formatting.Table(['counter', 'dateTime', 'type'])

    if not any([start_date, end_date, valid_type, summary_period]):
        raise exceptions.ArgumentError(
            "Must provide [--start_date], [--end_date], [--valid_type], or [--summary_period] to retrieve the usage "
            "information")

    vs_id = helpers.resolve_id(vsi.resolve_ids, identifier, 'VS')

    result = vsi.get_summary_data_usage(instance_id=vs_id, start_date=start_date, end_date=end_date,
                                        valid_type=valid_type, summary_period=summary_period)

    for data in result:
        table.add_row([
            data['counter'],
            data['dateTime'],
            data['type'],
        ])

    env.fout(table)
