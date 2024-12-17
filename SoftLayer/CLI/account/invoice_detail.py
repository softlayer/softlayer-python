"""Invoice details"""
# :license: MIT, see LICENSE for more details.

import click

from SoftLayer.CLI.command import SLCommand as SLCommand
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.managers.account import AccountManager as AccountManager
from SoftLayer import utils


@click.command(cls=SLCommand)
@click.argument('identifier')
@click.option('--details', is_flag=True, default=False, show_default=True,
              help="Shows a very detailed list of charges")
@environment.pass_env
def cli(env, identifier, details):
    """Invoice details

    Will display the top level invoice items for a given invoice. The cost displayed is the sum of the item's
    cost along with all its child items.
    The --details option will display any child items a top level item may have. Parent items will appear
    in this list as well to display their specific cost.
    """

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
        total_recur, total_single = sum_item_charges(item)
        table.add_row([
            item.get('id'),
            category,
            nice_string(description),
            f"${total_single:,.2f}",
            f"${total_recur:,.2f}",
            utils.clean_time(item.get('createDate'), out_format="%Y-%m-%d"),
            utils.lookup(item, 'location', 'name')
        ])
        if details:
            # This item has children, so we want to print out the parent item too. This will match the
            # invoice from the portal. https://github.com/softlayer/softlayer-python/issues/2201
            if len(item.get('children')) > 0:
                single = float(item.get('oneTimeAfterTaxAmount', 0.0))
                recurring = float(item.get('recurringAfterTaxAmount', 0.0))
                table.add_row([
                    '>>>',
                    category,
                    nice_string(description),
                    f"${single:,.2f}",
                    f"${recurring:,.2f}",
                    '---',
                    '---'
                ])
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


def sum_item_charges(item: dict) -> (float, float):
    """Takes a billing Item, sums up its child items and returns recurring, one_time prices"""

    # API returns floats as strings in this case
    single = float(item.get('oneTimeAfterTaxAmount', 0.0))
    recurring = float(item.get('recurringAfterTaxAmount', 0.0))
    for child in item.get('children', []):
        single = single + float(child.get('oneTimeAfterTaxAmount', 0.0))
        recurring = recurring + float(child.get('recurringAfterTaxAmount', 0.0))

    return (recurring, single)
