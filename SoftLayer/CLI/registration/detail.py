"""Get details for a subnet registration."""
# :license: MIT, see LICENSE for more details.

import click

from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.managers.registration import RegistrationManager


@click.command()
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """Get details for a subnet registration.

    """

    env.registerClient = RegistrationManager(env.client)
    register = env.registerClient.detail(identifier)

    table = formatting.KeyValueTable(['name', 'value'])
    table.align['name'] = 'r'
    table.align['value'] = 'l'
    table.add_row(['id', register['id']])
    table.add_row(['createDate', register['createDate']])
    table.add_row(['companyName', register['account']['companyName']])
    table.add_row(['Name', register['account']['firstName'] + ' ' + register['account']['lastName']])
    table.add_row(['AccountId', register['accountId']])
    table.add_row(['email', register['account']['email']])
    table.add_row(['officePhone', register['account']['officePhone']])
    table.add_row(['address1', register['account']['address1']])
    table.add_row(['networkIdentifier', register['networkIdentifier']])
    table.add_row(['cidr', register['cidr']])
    table.add_row(['detailType', register['personDetail']['detailType']['keyName']])
    table.add_row(['networkDetail', register['networkDetail']['detailType']['keyName']])
    table.add_row(['status', register['statusId']])
    env.fout(table)
