"""List origin pull mappings."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting


@click.command()
@click.argument('unique_id')
@environment.pass_env
def cli(env, unique_id):
    """List origin path for an existing CDN mapping."""

    manager = SoftLayer.CDNManager(env.client)
    origins = manager.get_origins(unique_id)

    table = formatting.Table(['Path', 'Origin', 'HTTP Port', 'Status'])

    for origin in origins:
        table.add_row([origin['path'],
                       origin['origin'],
                       origin['httpPort'],
                       origin['status']])

    env.fout(table)
