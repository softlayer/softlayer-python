"""List SoftLayer Message Queue Endpoints."""
# :license: MIT, see LICENSE for more details.

import softlayer
from softlayer.cli import environment
from softlayer.cli import formatting

import click


@click.command()
@environment.pass_env
def cli(env):
    """List SoftLayer Message Queue Endpoints."""

    manager = softlayer.MessagingManager(env.client)
    regions = manager.get_endpoints()

    table = formatting.Table(['name', 'public', 'private'])
    for region, endpoints in regions.items():
        table.add_row([
            region,
            endpoints.get('public') or formatting.blank(),
            endpoints.get('private') or formatting.blank(),
        ])

    return table
