"""Get all hardware notifications associated with the passed hardware ID."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """Get all hardware notifications."""

    hardware = SoftLayer.HardwareManager(env.client)

    notifications = hardware.get_notifications(identifier)

    table = formatting.KeyValueTable(['Id', 'Domain', 'Hostmane', 'Username', 'Email', 'FirstName', 'Lastname'])
    table.align['Domain'] = 'r'
    table.align['Username'] = 'l'

    for notification in notifications:
        table.add_row([notification['id'],
                       notification['hardware']['fullyQualifiedDomainName'], notification['hardware']['hostname'],
                       notification['user']['username'], notification['user']['email'],
                       notification['user']['firstName'], notification['user']['lastName']])

    env.fout(table)
