"""List Object Storage accounts."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting


@click.command()
@environment.pass_env
def cli(env):
    """List object storage accounts."""

    mgr = SoftLayer.ObjectStorageManager(env.client)
    accounts = mgr.list_accounts()
    table = formatting.Table(['id', 'name'])
    table.sortby = 'id'
    for account in accounts:
        table.add_row([
            account['id'],
            account['username'],
        ])

    env.fout(table)
