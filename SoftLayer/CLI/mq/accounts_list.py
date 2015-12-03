"""List SoftLayer Message Queue Accounts."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting


@click.command()
@environment.pass_env
def cli(env):
    """List SoftLayer Message Queue Accounts."""

    manager = SoftLayer.MessagingManager(env.client)
    accounts = manager.list_accounts()

    table = formatting.Table(['id', 'name', 'status'])
    for account in accounts:
        if not account['nodes']:
            continue

        table.add_row([account['nodes'][0]['accountName'],
                       account['name'],
                       account['status']['name']])

    env.fout(table)
