"""Provides some details related to the order."""
# :license: MIT, see LICENSE for more details.

import click

from SoftLayer.CLI.account.invoice_detail import get_invoice_table

from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.managers import ordering
from SoftLayer import utils


@click.command()
@click.argument('identifier')
@click.option('--details', is_flag=True, default=False, show_default=True,
              help="Shows a very detailed list of charges")
@environment.pass_env
def cli(env, identifier, details):
    """Provides some details related to order owner, date order, cost information, initial invoice."""

    manager = ordering.OrderingManager(env.client)
    order = manager.get_order_detail(identifier)
    order_table = get_order_table(order)

    invoice = order.get('initialInvoice', {})
    top_items = invoice.get('invoiceTopLevelItems', [])
    invoice_id = invoice.get('id')
    invoice_table = get_invoice_table(invoice_id, top_items, details)

    order_table.add_row(['Initial Invoice', invoice_table])

    env.fout(order_table)


def get_order_table(order):
    """Formats a table for billing order"""

    title = "Order {id}".format(id=order.get('id'))
    date_format = '%Y-%m-%d'
    table = formatting.Table(["Key", "Value"], title=title)
    table.align = 'l'

    ordered_by = "IBM"
    user = order.get('userRecord', None)
    if user:
        ordered_by = "{} ({})".format(user.get('displayName'), utils.lookup(user, 'userStatus', 'name'))
    table.add_row(['Ordered By', ordered_by])

    table.add_row(['Create Date', utils.clean_time(order.get('createDate'), date_format, date_format)])
    table.add_row(['Modify Date', utils.clean_time(order.get('modifyDate'), date_format, date_format)])
    table.add_row(['Order Approval Date', utils.clean_time(order.get('orderApprovalDate'), date_format, date_format)])
    table.add_row(['Status', order.get('status')])
    table.add_row(['Order Total Amount', "{price:.2f}".format(price=float(order.get('orderTotalAmount', '0')))])
    table.add_row(['Invoice Total Amount', "{price:.2f}".
                  format(price=float(order.get('initialInvoice', {}).get('invoiceTotalAmount', '0')))])

    items = order.get('items', [])
    item_table = formatting.Table(["Item Description"])
    item_table.align['description'] = 'l'

    for item in items:
        item_table.add_row([item.get('description')])

    table.add_row(['Items', item_table])

    return table
