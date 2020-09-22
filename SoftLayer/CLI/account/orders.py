"""Order list account"""
# :license: MIT, see LICENSE for more details.

import click

from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.managers.account import AccountManager as AccountManager
from SoftLayer import utils


@click.command()
@click.option('--limit', '-l',
              help='How many results to get in one api call, default is 100',
              default=100,
              show_default=True)
@environment.pass_env
def cli(env, limit):
    """Order list account."""
    manager = AccountManager(env.client)
    orders = manager.get_account_all_billing_orders(limit)

    table = []
    order_table = formatting.Table(['id', 'State', 'user', 'PurchaseDate', 'orderTotalAmount', 'Items'],
                                   title="orders")
    order_table.sortby = 'orderTotalAmount'
    order_table.align = 'l'

    for order in orders:
        items = []
        for item in order['items']:
            items.append(item['description'])
        create_date = utils.clean_time(order['createDate'], in_format='%Y-%m-%d', out_format='%Y-%m-%d')

        order_table.add_row([order['id'], order['status'], order['userRecord']['username'], create_date,
                             order['orderTotalAmount'], utils.trim_to(' '.join(map(str, items)), 50)])
    table.append(order_table)
    env.fout(formatting.listing(table, separator='\n'))
