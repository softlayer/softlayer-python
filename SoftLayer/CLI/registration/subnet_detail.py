"""Get details for a subnet registration."""
# :license: MIT, see LICENSE for more details.

import click

from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.CLI import exceptions
from SoftLayer.managers.registration import RegistrationManager


@click.command()
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """Get details for a subnet registration."""

    env.registerClient = RegistrationManager(env.client)
    registration = env.registerClient.detail(identifier)

    if not registration:
        raise exceptions.CLIAbort(
            'No Active Registration found for this Subnet'
        )

    table = formatting.KeyValueTable(['name', 'value'])
    table.align['name'] = 'r'
    table.align['value'] = 'l'
    table.add_row(['id', registration['id']])
    table.add_row(['createDate', registration['createDate']])
    table.add_row(['companyName', registration['account']['companyName']])
    table.add_row(['Name', registration['account']['firstName'] + ' ' + registration['account']['lastName']])
    table.add_row(['AccountId', registration['accountId']])
    table.add_row(['email', registration['account']['email']])
    table.add_row(['officePhone', registration['account']['officePhone']])
    table.add_row(['address', registration['account']['address1']])
    table.add_row(['networkIdentifier', registration['networkIdentifier']])
    table.add_row(['cidr', registration['cidr']])
    table.add_row(['detailType', registration['personDetail']['detailType']['keyName']])
    table.add_row(['networkDetail', registration['networkDetail']['detailType']['keyName']])
    table.add_row(['status', registration['statusId']])
    env.fout(table)
