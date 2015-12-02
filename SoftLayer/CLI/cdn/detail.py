"""Detail a CDN Account."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting


@click.command()
@click.argument('account_id')
@environment.pass_env
def cli(env, account_id):
    """Detail a CDN Account."""

    manager = SoftLayer.CDNManager(env.client)
    account = manager.get_account(account_id)

    table = formatting.KeyValueTable(['name', 'value'])
    table.align['name'] = 'r'
    table.align['value'] = 'l'

    table.add_row(['id', account['id']])
    table.add_row(['account_name', account['cdnAccountName']])
    table.add_row(['type', account['cdnSolutionName']])
    table.add_row(['status', account['status']['name']])
    table.add_row(['created', account['createDate']])
    table.add_row(['notes',
                   account.get('cdnAccountNote', formatting.blank())])

    env.fout(table)
