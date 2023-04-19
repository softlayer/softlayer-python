"""Lists account orders."""
# :license: MIT, see LICENSE for more details.

import click

from SoftLayer.CLI.command import SLCommand as SLCommand
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.managers.account import AccountManager as AccountManager
from SoftLayer import utils


def upgrade_table(upgrades):
    """Formats a table for upgrade orders"""
    table = formatting.Table(['Id', 'Maintance window', 'Status', 'Created Date',
                              'Case'], title="Upgrade orders")
    table.align['Subject'] = 'l'
    table.align['Impacted Resources'] = 'l'
    for upgrade in upgrades:
        table.add_row([upgrade.get('id'),
                       upgrade.get('maintenanceStartTimeUtc'),
                       upgrade.get('statusId'),
                       upgrade.get('createDate'),
                       upgrade.get('ticketId') or '--'])
    return table


@click.command(cls=SLCommand)
@click.option('--limit', '-l',
              help='How many results to get in one api call',
              default=100,
              show_default=True)
@click.option('--upgrades', is_flag=True, default=False,
              help="Show upgrades orders.")
@environment.pass_env
def cli(env, limit, upgrades):
    """Lists account orders. Use `slcli order lookup <ID>` to find more details about a specific order."""
    manager = AccountManager(env.client)
    orders = manager.get_account_all_billing_orders(limit)
    upgrade = manager.get_account_upgrade_orders(limit)

    order_table = formatting.Table(['Id', 'State', 'User', 'Date', 'Amount', 'Item'],
                                   title="orders")
    order_table.align = 'l'

    for order in orders:
        items = []
        for item in order['items']:
            items.append(item['description'])
        create_date = utils.clean_time(order['createDate'], in_format='%Y-%m-%d', out_format='%Y-%m-%d')

        order_table.add_row([order['id'], order['status'], order['userRecord']['username'], create_date,
                             order['orderTotalAmount'], utils.trim_to(' '.join(map(str, items)), 50)])
    env.fout(order_table)
    if upgrades:
        env.fout(upgrade_table(upgrade))
