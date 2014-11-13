"""Create a zone."""
# :license: MIT, see LICENSE for more details.

import softlayer
from softlayer.cli import environment

import click


@click.command()
@click.argument('zone')
@environment.pass_env
def cli(env, zone):
    """Create a zone."""

    manager = softlayer.DNSManager(env.client)
    manager.create_zone(zone)
