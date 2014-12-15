"""Detail a CDN Account."""
# :license: MIT, see LICENSE for more details.

import softlayer
from softlayer.cli import environment
from softlayer.cli import formatting

import click


@click.command()
@click.argument('account_id')
@environment.pass_env
def cli(env, account_id):
    """Detail a CDN Account."""

    manager = softlayer.CDNManager(env.client)
    account = manager.get_account(account_id)

    table = formatting.KeyValueTable(['Name', 'Value'])
    table.align['Name'] = 'r'
    table.align['Value'] = 'l'

    table.add_row(['id', account['id']])
    table.add_row(['account_name', account['cdnAccountName']])
    table.add_row(['type', account['cdnSolutionName']])
    table.add_row(['status', account['status']['name']])
    table.add_row(['created', account['createDate']])
    table.add_row(['notes',
                   account.get('cdnAccountNote', formatting.blank())])

    return table
