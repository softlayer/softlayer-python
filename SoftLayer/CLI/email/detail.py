"""Display details for a specified email account."""
# :license: MIT, see LICENSE for more details.

import click
from SoftLayer.CLI.email.list import build_statistics_table
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.managers.email import EmailManager
from SoftLayer import utils


@click.command()
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """Display details for a specified email."""

    email_manager = EmailManager(env.client)
    result = email_manager.get_instance(identifier)

    table = formatting.KeyValueTable(['name', 'value'])
    table.align['name'] = 'r'
    table.align['value'] = 'l'

    table.add_row(['id', result.get('id')])
    table.add_row(['username', result.get('username')])
    table.add_row(['email_address', result.get('emailAddress')])
    table.add_row(['create_date', result.get('createDate')])
    table.add_row(['category_code', utils.lookup(result, 'billingItem', 'categoryCode')])
    table.add_row(['description', utils.lookup(result, 'billingItem', 'description')])
    table.add_row(['type_description', utils.lookup(result, 'type', 'description')])
    table.add_row(['type', utils.lookup(result, 'type', 'keyName')])
    table.add_row(['vendor', utils.lookup(result, 'vendor', 'keyName')])

    statistics = email_manager.get_statistics(identifier)

    for statistic in statistics:
        table.add_row(['statistics', build_statistics_table(statistic)])

    env.fout(table)
