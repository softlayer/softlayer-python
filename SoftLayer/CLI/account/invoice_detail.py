"""Invoice details"""
# :license: MIT, see LICENSE for more details.

import click

from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.managers.account import AccountManager as AccountManager
from SoftLayer import utils


@click.command()
@click.argument('identifier')
@click.option('--details', is_flag=True, default=False, show_default=True,
              help="Shows a very detailed list of charges")
@environment.pass_env
def cli(env, identifier, details):
    """Invoice details"""

    manager = AccountManager(env.client)
    top_items = manager.get_billing_items(identifier)
    table = get_invoice_table(identifier, top_items, details)
    env.fout(table)


def nice_string(ugly_string, limit=100):
    """Format and trims strings"""
    return (ugly_string[:limit] + '..') if len(ugly_string) > limit else ugly_string


def get_invoice_table(identifier, top_items, details):
    """Formats a table for invoice top level items.

     :param int identifier: Invoice identifier.
     :param list top_items: invoiceTopLevelItems.
     :param bool details: To add very detailed list of charges.
      """

    title = "Invoice %s" % identifier
    table = formatting.Table(["Item Id", "Category", "Description", "Single",
                              "Monthly", "Create Date", "Location"], title=title)
    table.align['category'] = 'l'
    table.align['description'] = 'l'
    for item in top_items:
        fqdn = "%s.%s" % (item.get('hostName', ''), item.get('domainName', ''))
        # category id=2046, ram_usage doesn't have a name...
        category = utils.lookup(item, 'category', 'name') or item.get('categoryCode')
        description = nice_string(item.get('description'))
        if fqdn != '.':
            description = "%s (%s)" % (item.get('description'), fqdn)
        table.add_row([
            item.get('id'),
            category,
            nice_string(description),
            "$%.2f" % float(item.get('oneTimeAfterTaxAmount')),
            "$%.2f" % float(item.get('recurringAfterTaxAmount')),
            utils.clean_time(item.get('createDate'), out_format="%Y-%m-%d"),
            utils.lookup(item, 'location', 'name')
        ])
        if details:
            for child in item.get('children', []):
                table.add_row([
                    '>>>',
                    utils.lookup(child, 'category', 'name'),
                    nice_string(child.get('description')),
                    "$%.2f" % float(child.get('oneTimeAfterTaxAmount')),
                    "$%.2f" % float(child.get('recurringAfterTaxAmount')),
                    '---',
                    '---'
                ])
    return table
