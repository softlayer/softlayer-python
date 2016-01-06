"""List CDN Accounts."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting


@click.command()
@click.option('--sortby',
              help='Column to sort by',
              type=click.Choice(['id',
                                 'datacenter',
                                 'host',
                                 'cores',
                                 'memory',
                                 'primary_ip',
                                 'backend_ip']))
@environment.pass_env
def cli(env, sortby):
    """List all CDN accounts."""

    manager = SoftLayer.CDNManager(env.client)
    accounts = manager.list_accounts()

    table = formatting.Table(['id',
                              'account_name',
                              'type',
                              'created',
                              'notes'])
    for account in accounts:
        table.add_row([
            account['id'],
            account['cdnAccountName'],
            account['cdnSolutionName'],
            account['createDate'],
            account.get('cdnAccountNote', formatting.blank())
        ])

    table.sortby = sortby
    env.fout(table)
