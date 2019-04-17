"""View a quote"""
# :license: MIT, see LICENSE for more details.
import click

from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.managers import ordering
from SoftLayer.utils import lookup


@click.command()
@click.argument('quote')
@environment.pass_env
def cli(env, quote):
    """View a quote"""

    manager = ordering.OrderingManager(env.client)
    result = manager.get_quote_details(quote)

    package = result['order']['items'][0]['package']
    title = "{} - Package: {}, Id {}".format(result.get('name'), package['keyName'], package['id'])
    table = formatting.Table([
        'Category', 'Description', 'Quantity', 'Recurring', 'One Time'
    ], title=title)
    table.align['Category'] = 'l'
    table.align['Description'] = 'l'

    items = lookup(result, 'order', 'items')
    for item in items:
        table.add_row([
            item.get('categoryCode'),
            item.get('description'),
            item.get('quantity'),
            item.get('recurringFee'),
            item.get('oneTimeFee')
        ])

    env.fout(table)
