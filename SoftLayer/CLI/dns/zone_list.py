"""List all zones."""
# :license: MIT, see LICENSE for more details.

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting

import click


@click.command()
@environment.pass_env
def cli(env):
    """List all zones."""

    manager = SoftLayer.DNSManager(env.client)
    zones = manager.list_zones()
    table = formatting.Table(['id', 'zone', 'serial', 'updated'])
    table.align['serial'] = 'c'
    table.align['updated'] = 'c'

    for zone in zones:
        table.add_row([
            zone['id'],
            zone['name'],
            zone['serial'],
            zone['updateDate'],
        ])

    return table
