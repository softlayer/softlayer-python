"""Create a zone."""
# :license: MIT, see LICENSE for more details.

import SoftLayer
from SoftLayer.CLI import environment

import click


@click.command()
@click.argument('zone')
@environment.pass_env
def cli(env, zone):
    """Create a zone."""

    manager = SoftLayer.DNSManager(env.client)
    manager.create_zone(zone)
