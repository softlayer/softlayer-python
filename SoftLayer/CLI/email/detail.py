"""Display details for a specified email."""
# :license: MIT, see LICENSE for more details.

import click
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
    table.add_row(['create_date', result.get('createDate')])
    table.add_row(['categoryCode', utils.lookup(result, 'billingItem', 'categoryCode')])
    table.add_row(['description', utils.lookup(result, 'billingItem', 'description')])
    table.add_row(['type_description', utils.lookup(result, 'type', 'description')])
    table.add_row(['type', utils.lookup(result, 'type', 'keyName')])
    table.add_row(['vendor', utils.lookup(result, 'vendor', 'keyName')])

    env.fout(table)
