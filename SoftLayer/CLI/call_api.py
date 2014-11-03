"""Call arbitrary API endpoints."""

import click

from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting


@click.command('call', short_help="Call arbitrary API endpoints.")
@click.argument('service')
@click.argument('method')
@click.option('--id', '_id', help="Init parameter")
@click.option('--mask', help="String-based object mask")
@click.option('--limit', type=click.INT, help="Result limit")
@click.option('--offset', type=click.INT, help="Result offset")
@environment.pass_env
def cli(env, service, method, _id, mask, limit, offset):
    """Call arbitrary API endpoints with the given SERVICE and METHOD.

    \b
    Examples:
    sl call-api Account getObject
    sl call-api Account getVirtualGuests --limit=10 --mask=id,hostname
    sl call-api Virtual_Guest getObject --id=2710344
    """
    result = env.client.call(service, method,
                             id=_id,
                             mask=mask,
                             limit=limit,
                             offset=offset)
    return format_api_result(result)


def format_api_result(value):
    """Convert raw API responses to response tables."""
    if isinstance(value, list):
        return format_api_list(value)
    if isinstance(value, dict):
        return format_api_dict(value)
    return value


def format_api_dict(result):
    """Format dictionary responses into key-value table."""

    table = formatting.KeyValueTable(['Name', 'Value'])
    table.align['Name'] = 'r'
    table.align['Value'] = 'l'

    for key, value in result.items():
        value = format_api_result(value)
        table.add_row([key, value])

    return table


def format_api_list(result):
    """Format list responses into a table."""
    # Gather all unique keys from every value
    # Note(kmcdonald): This assumes we only return lists of objects.
    all_keys = set()
    for item in result:
        all_keys = all_keys.union(item.keys())

    all_keys = sorted(all_keys)
    table = formatting.Table(all_keys)

    for item in result:
        values = []
        for key in all_keys:
            value = format_api_result(item.get(key))
            values.append(value)

        table.add_row(values)

    return table
