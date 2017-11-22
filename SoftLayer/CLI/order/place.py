"""Verify or place an order."""
# :license: MIT, see LICENSE for more details.

import json

import click

from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer.managers import ordering

COLUMNS = ['keyName',
           'description',
           'cost', ]


@click.command()
@click.argument('package_keyname')
@click.argument('location')
@click.option('--preset',
              help="The order preset (if required by the package)")
@click.option('--verify',
              is_flag=True,
              help="Flag denoting whether or not to only verify the order, not place it")
@click.option('--billing',
              type=click.Choice(['hourly', 'monthly']),
              default='hourly',
              show_default=True,
              help="Billing rate")
@click.option('--extras',
              help="JSON string denoting extra data that needs to be sent with the order")
@click.argument('order_items', nargs=-1)
@environment.pass_env
def cli(env, package_keyname, location, preset, verify, billing, extras, order_items):
    """Place or verify an order."""
    manager = ordering.OrderingManager(env.client)

    if extras:
        extras = json.loads(extras)

    args = (package_keyname, location, order_items)
    kwargs = {'preset_keyname': preset,
              'extras': extras,
              'quantity': 1,
              'hourly': True if billing == 'hourly' else False}

    if verify:
        table = formatting.Table(COLUMNS)
        order_to_place = manager.verify_order(*args, **kwargs)
        for price in order_to_place['prices']:
            cost_key = 'hourlyRecurringFee' if billing == 'hourly' else 'recurringFee'
            table.add_row([
                price['item']['keyName'],
                price['item']['description'],
                price[cost_key] if cost_key in price else formatting.blank()
            ])

    else:
        if not (env.skip_confirmations or formatting.confirm(
                "This action will incur charges on your account. Continue?")):
            raise exceptions.CLIAbort("Aborting order.")

        order = manager.place_order(*args, **kwargs)

        table = formatting.KeyValueTable(['name', 'value'])
        table.align['name'] = 'r'
        table.align['value'] = 'l'
        table.add_row(['id', order['orderId']])
        table.add_row(['created', order['orderDate']])
        table.add_row(['status', order['placedOrder']['status']])
    env.fout(table)
