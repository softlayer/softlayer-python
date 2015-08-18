"""Call arbitrary API endpoints."""

import click

from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting


@click.command('call', short_help="Call arbitrary API endpoints.")
@click.argument('service')
@click.argument('method')
@click.argument('parameters', nargs=-1)
@click.option('--id', '_id', help="Init parameter")
@click.option('--mask', help="String-based object mask")
@click.option('--limit', type=click.INT, help="Result limit")
@click.option('--offset', type=click.INT, help="Result offset")
@environment.pass_env
def cli(env, service, method, parameters, _id, mask, limit, offset):
    """Call arbitrary API endpoints with the given SERVICE and METHOD.

    \b
    Examples:
    slcli call-api Account getObject
    slcli call-api Account getVirtualGuests --limit=10 --mask=id,hostname
    slcli call-api Virtual_Guest getObject --id=12345
    slcli call-api Metric_Tracking_Object getBandwidthData --id=1234 \\
        "2015-01-01 00:00:00" "2015-01-1 12:00:00" public
    """
    result = env.client.call(service, method, *parameters,
                             id=_id,
                             mask=mask,
                             limit=limit,
                             offset=offset)
    env.fout(formatting.iter_to_table(result))
