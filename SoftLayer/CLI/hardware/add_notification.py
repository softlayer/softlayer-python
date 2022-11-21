"""Create a user hardware notification entry."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.argument('identifier')
@click.option('--users', multiple=True, required=True,
              help='UserId to be notified on monitoring failure.')
@environment.pass_env
def cli(env, identifier, users):
    """Create a user hardware notification entry."""

    hardware = SoftLayer.HardwareManager(env.client)

    table = formatting.KeyValueTable(['Id', 'Hostmane', 'Username', 'Email', 'FirstName', 'Lastname'])
    table.align['Id'] = 'r'
    table.align['Username'] = 'l'

    for user in users:
        notification = hardware.add_notification(identifier, user)
        if notification:
            table.add_row([notification['id'], notification['hardware']['fullyQualifiedDomainName'],
                           notification['user']['username'], notification['user']['email'],
                           notification['user']['firstName'], notification['user']['lastName']])
        else:
            raise exceptions.CLIAbort("User not found: {}.".format(user))
    env.fout(table)
