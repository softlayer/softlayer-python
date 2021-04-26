"""Gets some details about a specific billing item."""
# :license: MIT, see LICENSE for more details.
import click

from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.managers.account import AccountManager as AccountManager
from SoftLayer import utils


@click.command()
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """Gets detailed information about a billing item."""
    manager = AccountManager(env.client)
    item = manager.get_item_detail(identifier)
    env.fout(item_table(item))


def item_table(item):
    """Formats a table for billing items"""

    date_format = '%Y-%m-%d'
    table = formatting.Table(["Key", "Value"], title="{}".format(item.get('description', 'Billing Item')))
    table.add_row(['createDate', utils.clean_time(item.get('createDate'), date_format, date_format)])
    table.add_row(['cycleStartDate', utils.clean_time(item.get('cycleStartDate'), date_format, date_format)])
    table.add_row(['cancellationDate', utils.clean_time(item.get('cancellationDate'), date_format, date_format)])
    table.add_row(['description', item.get('description')])
    table.align = 'l'
    fqdn = "{}.{}".format(item.get('hostName'), item.get('domain'))
    if fqdn != ".":
        table.add_row(['FQDN', fqdn])

    if item.get('hourlyFlag', False):
        table.add_row(['hourlyRecurringFee', item.get('hourlyRecurringFee')])
        table.add_row(['hoursUsed', item.get('hoursUsed')])
        table.add_row(['currentHourlyCharge', item.get('currentHourlyCharge')])
    else:
        table.add_row(['recurringFee', item.get('recurringFee')])

    ordered_by = "IBM"
    user = utils.lookup(item, 'orderItem', 'order', 'userRecord')
    if user:
        ordered_by = "{} ({})".format(user.get('displayName'), utils.lookup(user, 'userStatus', 'name'))
    table.add_row(['Ordered By', ordered_by])
    table.add_row(['Notes', item.get('notes')])
    table.add_row(['Location', utils.lookup(item, 'location', 'name')])
    if item.get('children'):
        for child in item.get('children'):
            table.add_row([child.get('categoryCode'), child.get('description')])

    return table
