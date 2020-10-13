"""List CDN Accounts."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting


@click.command()
@click.option('--sortby',
              help='Column to sort by',
              type=click.Choice(['unique_id',
                                 'domain',
                                 'origin',
                                 'vendor',
                                 'cname',
                                 'status']))
@environment.pass_env
def cli(env, sortby):
    """List all CDN accounts."""

    manager = SoftLayer.CDNManager(env.client)
    accounts = manager.list_cdn()

    table = formatting.Table(['unique_id',
                              'domain',
                              'origin',
                              'vendor',
                              'cname',
                              'status'])
    for account in accounts:
        table.add_row([
            account['uniqueId'],
            account['domain'],
            account['originHost'],
            account['vendorName'],
            account['cname'],
            account['status']
        ])

    table.sortby = sortby
    env.fout(table)
