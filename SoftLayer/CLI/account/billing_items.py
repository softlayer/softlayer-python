"""Lists all active billing items on this account. See https://cloud.ibm.com/billing/billing-items"""
# :license: MIT, see LICENSE for more details.
import click

from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.managers.account import AccountManager as AccountManager
from SoftLayer import utils


@click.command()
@environment.pass_env
def cli(env):
    """Lists billing items with some other useful information.

    Similiar to https://cloud.ibm.com/billing/billing-items
    """

    manager = AccountManager(env.client)
    items = manager.get_account_billing_items()
    table = item_table(items)

    env.fout(table)


def item_table(items):
    """Formats a table for billing items"""
    table = formatting.Table([
        "Id",
        "Create Date",
        "Cost",
        "Category Code",
        "Ordered By",
        "Description",
        "Notes"
    ], title="Billing Items")
    table.align['Description'] = 'l'
    table.align['Category Code'] = 'l'
    for item in items:
        description = item.get('description')
        fqdn = "{}.{}".format(item.get('hostName', ''), item.get('domainName', ''))
        if fqdn != ".":
            description = fqdn
        user = utils.lookup(item, 'orderItem', 'order', 'userRecord')
        ordered_by = "IBM"
        create_date = utils.clean_time(item.get('createDate'), in_format='%Y-%m-%d', out_format='%Y-%m-%d')
        if user:
            # ordered_by = "{} ({})".format(user.get('displayName'), utils.lookup(user, 'userStatus', 'name'))
            ordered_by = user.get('displayName')

        table.add_row([
            item.get('id'),
            create_date,
            item.get('nextInvoiceTotalRecurringAmount'),
            item.get('categoryCode'),
            ordered_by,
            utils.trim_to(description, 50),
            utils.trim_to(item.get('notes', 'None'), 40),
        ])
    return table
