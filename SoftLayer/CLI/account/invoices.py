"""Invoice listing"""
# :license: MIT, see LICENSE for more details.

import click

from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.managers.account import AccountManager as AccountManager
from SoftLayer import utils


@click.command()
@click.option('--limit', default=50, show_default=True,
              help="How many invoices to get back.")
@click.option('--closed', is_flag=True, default=False, show_default=True,
              help="Include invoices with a CLOSED status.")
@click.option('--all', 'get_all', is_flag=True, default=False, show_default=True,
              help="Return ALL invoices. There may be a lot of these.")
@environment.pass_env
def cli(env, limit, closed=False, get_all=False):
    """List invoices"""

    manager = AccountManager(env.client)
    invoices = manager.get_invoices(limit, closed, get_all)

    table = formatting.Table([
        "Id", "Created", "Type", "Status", "Starting Balance", "Ending Balance", "Invoice Amount", "Items"
    ])
    table.align['Starting Balance'] = 'l'
    table.align['Ending Balance'] = 'l'
    table.align['Invoice Amount'] = 'l'
    table.align['Items'] = 'l'
    if isinstance(invoices, dict):
        invoices = [invoices]
    for invoice in invoices:
        table.add_row([
            invoice.get('id'),
            utils.clean_time(invoice.get('createDate'), out_format="%Y-%m-%d"),
            invoice.get('typeCode'),
            invoice.get('statusCode'),
            invoice.get('startingBalance'),
            invoice.get('endingBalance'),
            invoice.get('invoiceTotalAmount'),
            invoice.get('itemCount')
        ])
    env.fout(table)
