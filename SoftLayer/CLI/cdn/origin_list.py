"""List origin pull mappings."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting


@click.command()
@click.argument('account_id')
@environment.pass_env
def cli(env, account_id):
    """List origin pull mappings."""

    manager = SoftLayer.CDNManager(env.client)
    origins = manager.get_origins(account_id)

    table = formatting.Table(['id', 'media_type', 'cname', 'origin_url'])

    for origin in origins:
        table.add_row([origin['id'],
                       origin['mediaType'],
                       origin.get('cname', formatting.blank()),
                       origin['originUrl']])

    env.fout(table)
