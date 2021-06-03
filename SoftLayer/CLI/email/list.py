"""Lists Email Delivery Service """
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
    table.align['name'] = 'r'
    table.align['value'] = 'l'
    table_information = formatting.KeyValueTable(['id', 'username', 'hostname', 'description', 'vendor'])
    table_information.align['id'] = 'r'
    table_information.align['username'] = 'l'

    for email in result:
        table_information.add_row([email.get('id'), email.get('username'), email.get('emailAddress'),
                                   utils.lookup(email, 'type', 'description'),
                                   utils.lookup(email, 'vendor', 'keyName')])

        overview_table = _build_overview_table(email_manager.get_account_overview(email.get('id')))
        statistics = email_manager.get_statistics(email.get('id'))

        table.add_row(['email_information', table_information])
        table.add_row(['email_overview', overview_table])
        for statistic in statistics:
            table.add_row(['statistics', build_statistics_table(statistic)])

    env.fout(table)


def _build_overview_table(email_overview):
    table = formatting.Table(
        ['credit_allowed', 'credits_remain', 'credits_overage', 'credits_used',
         'package', 'reputation', 'requests'])
    table.align['name'] = 'r'
    table.align['value'] = 'l'

    table.add_row([email_overview.get('creditsAllowed'), email_overview.get('creditsRemain'),
                   email_overview.get('creditsOverage'), email_overview.get('creditsUsed'),
                   email_overview.get('package'), email_overview.get('reputation'),
                   email_overview.get('requests')])

    return table


def build_statistics_table(statistics):
    """statistics records of Email Delivery account"""
    table = formatting.Table(['delivered', 'requests', 'bounces', 'opens', 'clicks', 'spam_reports'])
    table.align['name'] = 'r'
    table.align['value'] = 'l'

    table.add_row([statistics.get('delivered'), statistics.get('requests'),
                   statistics.get('bounces'), statistics.get('opens'),
                   statistics.get('clicks'), statistics.get('spamReports')])

    return table
