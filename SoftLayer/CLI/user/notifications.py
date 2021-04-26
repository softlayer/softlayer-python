"""List user notifications"""
import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting


@click.command()
@environment.pass_env
def cli(env):
    """My Notifications."""

    mgr = SoftLayer.UserManager(env.client)

    all_notifications = mgr.get_all_notifications()

    env.fout(notification_table(all_notifications))


def notification_table(all_notifications):
    """Creates a table of available notifications"""

    table = formatting.Table(['Id', 'Name', 'Description', 'Enabled'])
    table.align['Id'] = 'l'
    table.align['Name'] = 'l'
    table.align['Description'] = 'l'
    table.align['Enabled'] = 'l'
    for notification in all_notifications:
        table.add_row([notification['id'],
                       notification['name'],
                       notification['description'],
                       notification['enabled']])
    return table
