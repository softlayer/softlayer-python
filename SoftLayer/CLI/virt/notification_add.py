"""Create a user virtual notification entry."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.argument('identifier')
@click.option('--users', multiple=True,
              help='UserId to be notified on monitoring failure.')
@environment.pass_env
def cli(env, identifier, users):
    """Create a user virtual notification entry."""

    virtual = SoftLayer.VSManager(env.client)

    table = formatting.KeyValueTable(['Id', 'Hostmane', 'Username', 'Email', 'FirstName', 'Lastname'])
    table.align['Id'] = 'r'
    table.align['Username'] = 'l'

    for user in users:
        notification = virtual.add_notification(identifier, user)
        table.add_row([notification['id'], notification['guest']['fullyQualifiedDomainName'],
                       notification['user']['username'], notification['user']['email'],
                       notification['user']['lastName'], notification['user']['firstName']])

    env.fout(table)
