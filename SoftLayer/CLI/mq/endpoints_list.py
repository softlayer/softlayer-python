"""List SoftLayer Message Queue Endpoints."""
# :license: MIT, see LICENSE for more details.

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting

import click


@click.command()
@environment.pass_env
def cli(env):
    """List SoftLayer Message Queue Endpoints."""

    manager = SoftLayer.MessagingManager(env.client)
    regions = manager.get_endpoints()

    table = formatting.Table(['name', 'public', 'private'])
    for region, endpoints in regions.items():
        table.add_row([
            region,
            endpoints.get('public') or formatting.blank(),
            endpoints.get('private') or formatting.blank(),
        ])

    return table
