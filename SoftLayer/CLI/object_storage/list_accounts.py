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
    table = formatting.Table(['id', 'name', 'apiType'])
    table.sortby = 'id'
    global api_type
    for account in accounts:
        if 'vendorName' in account and 'Swift' == account['vendorName']:
            api_type = 'Swift'
        elif 'Cleversafe' in account['serviceResource']['name']:
            api_type = 'S3'

        table.add_row([
            account['id'],
            account['username'],
            api_type,
        ])

    env.fout(table)
