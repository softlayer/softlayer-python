"""Get details for a hardware device."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers
from SoftLayer import utils


@click.command()
@click.argument('identifier')
@click.option('--start_date', '-s', type=click.STRING, required=True,
              help="Start Date YYYY-MM-DD, YYYY-MM-DDTHH:mm:ss,")
@click.option('--end_date', '-e', type=click.STRING, required=True,
              help="End Date YYYY-MM-DD, YYYY-MM-DDTHH:mm:ss")
@click.option('--summary_period', '-p', type=click.INT, default=3600, show_default=True,
              help="300, 600, 1800, 3600, 43200 or 86400 seconds")
@click.option('--quite_summary', '-q', is_flag=True, default=False, show_default=True,
              help="Only show the summary table")
@environment.pass_env
def cli(env, identifier, start_date, end_date, summary_period, quite_summary):
    """Bandwidth data over date range. Bandwidth is listed in GB

    Using just a date might get you times off by 1 hour, use T00:01 to get just the specific days data
    Timezones can also be included with the YYYY-MM-DDTHH:mm:ss.00000-HH:mm format.

    Due to some rounding and date alignment details, results here might be slightly different than
    results in the control portal.

    Example::

        slcli hw bandwidth 1234 -s 2019-05-01T00:01 -e 2019-05-02T00:00:01.00000-12:00
    """
    vsi = SoftLayer.VSManager(env.client)
    vsi_id = helpers.resolve_id(vsi.resolve_ids, identifier, 'VS')
    data = vsi.get_bandwidth_data(vsi_id, start_date, end_date, None, summary_period)

    title = "Bandwidth Report: %s - %s" % (start_date, end_date)
    table, sum_table = create_bandwidth_table(data, summary_period, title)

    env.fout(sum_table)
    if not quite_summary:
        env.fout(table)


def create_bandwidth_table(data, summary_period, title="Bandwidth Report"):
    """Create 2 tables, bandwidth and sumamry. Used here and in hw bandwidth command"""

    formatted_data = {}
    for point in data:
        key = utils.clean_time(point['dateTime'])
        data_type = point['type']
        # conversion from byte to megabyte
        value = round(float(point['counter']) / 2 ** 20, 4)
        if formatted_data.get(key) is None:
            formatted_data[key] = {}
        formatted_data[key][data_type] = float(value)

    table = formatting.Table(['Date', 'Pub In', 'Pub Out', 'Pri In', 'Pri Out'], title=title)

    sum_table = formatting.Table(['Type', 'Sum GB', 'Average MBps', 'Max GB', 'Max Date'], title="Summary")

    # Required to specify keyName because getBandwidthTotals returns other counter types for some reason.
    bw_totals = [
        {'keyName': 'publicIn_net_octet', 'sum': 0.0, 'max': 0, 'name': 'Pub In'},
        {'keyName': 'publicOut_net_octet', 'sum': 0.0, 'max': 0, 'name': 'Pub Out'},
        {'keyName': 'privateIn_net_octet', 'sum': 0.0, 'max': 0, 'name': 'Pri In'},
        {'keyName': 'privateOut_net_octet', 'sum': 0.0, 'max': 0, 'name': 'Pri Out'},
    ]

    for key, value in formatted_data.items():
        new_row = [key]
        for bw_type in bw_totals:
            counter = value.get(bw_type['keyName'], 0)
            new_row.append(mb_to_gb(counter))
            bw_type['sum'] = bw_type['sum'] + counter
            if counter > bw_type['max']:
                bw_type['max'] = counter
                bw_type['maxDate'] = key
        table.add_row(new_row)

    for bw_type in bw_totals:
        total = bw_type.get('sum', 0.0)
        average = 0
        if total > 0:
            average = round(total / len(formatted_data) / summary_period, 4)
        sum_table.add_row([
            bw_type.get('name'),
            mb_to_gb(total),
            average,
            mb_to_gb(bw_type.get('max')),
            bw_type.get('maxDate')
        ])

    return table, sum_table


def mb_to_gb(mbytes):
    """Converts a MegaByte int to GigaByte. mbytes/2^10"""
    return round(mbytes / 2 ** 10, 4)
