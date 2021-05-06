"""Get lists Email Delivery account Service """
# :license: MIT, see LICENSE for more details.

import click

from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.managers.account import AccountManager
from SoftLayer.managers.email import EmailManager
from SoftLayer import utils


@click.command()
@environment.pass_env
def cli(env):
    """Lists Email Delivery Service """
    manager = AccountManager(env.client)
    email_manager = EmailManager(env.client)
    result = manager.get_network_message_delivery_accounts()

    table = formatting.KeyValueTable(['name', 'value'])

    table_information = formatting.KeyValueTable(['id', 'username', 'hostname', 'description', 'vendor'])
    table_information.align['id'] = 'r'
    table_information.align['username'] = 'l'

    for email in result:
        table_information.add_row([email.get('id'), email.get('username'), email.get('emailAddress'),
                                   utils.lookup(email, 'type', 'description'),
                                   utils.lookup(email, 'vendor', 'keyName')])

        overview_table = _build_overview_table(email_manager.get_account_overview(email.get('id')))
        statistics = email_manager.get_statistics(email.get('id'))

        table.add_row(['email information', table_information])
        table.add_row(['email overview', overview_table])
        for statistic in statistics:
            table.add_row(['statistics', _build_statistics_table(statistic)])

    env.fout(table)


def _build_overview_table(email_overview):
    table = formatting.Table(['name', 'value'])
    table.align['name'] = 'r'
    table.align['value'] = 'l'

    table.add_row(['creditsAllowed', email_overview.get('creditsAllowed')])
    table.add_row(['creditsRemain', email_overview.get('creditsRemain')])
    table.add_row(['package', email_overview.get('package')])
    table.add_row(['reputation', email_overview.get('reputation')])
    table.add_row(['requests', email_overview.get('requests')])

    return table


def _build_statistics_table(statistics):
    table = formatting.Table(['name', 'value'])
    table.align['name'] = 'r'
    table.align['value'] = 'l'

    table.add_row(['delivered', statistics.get('delivered')])
    table.add_row(['requests', statistics.get('requests')])
    table.add_row(['bounces', statistics.get('bounces')])
    table.add_row(['opens', statistics.get('opens')])
    table.add_row(['clicks', statistics.get('clicks')])
    table.add_row(['spam Reports', statistics.get('spamReports')])

    return table
