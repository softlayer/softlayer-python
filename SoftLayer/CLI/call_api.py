"""Call arbitrary API endpoints."""
import json

import click

from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting

# pylint: disable=unused-argument


def validate_filter(ctx, param, value):
    """Try to parse the given filter as a JSON string."""
    try:
        if value:
            return json.loads(value)
    except ValueError:
        raise click.BadParameter('filters need to be in JSON format')


@click.command('call', short_help="Call arbitrary API endpoints.")
@click.argument('service')
@click.argument('method')
@click.argument('parameters', nargs=-1)
@click.option('--id', '_id', help="Init parameter")
@click.option('--filter', '_filter',
              callback=validate_filter,
              help="Object filter in a JSON string")
@click.option('--mask', help="String-based object mask")
@click.option('--limit', type=click.INT, help="Result limit")
@click.option('--offset', type=click.INT, help="Result offset")
@environment.pass_env
def cli(env, service, method, parameters, _id, _filter, mask, limit, offset):
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
                             filter=_filter,
                             mask=mask,
                             limit=limit,
                             offset=offset)
    env.fout(formatting.iter_to_table(result))
