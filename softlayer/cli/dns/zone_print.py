"""Print zone in BIND format."""
# :license: MIT, see LICENSE for more details.

import softlayer
from softlayer.cli import environment
from softlayer.cli import helpers

import click


@click.command()
@click.argument('zone')
@environment.pass_env
def cli(env, zone):
    """Print zone in BIND format."""

    manager = softlayer.DNSManager(env.client)
    zone_id = helpers.resolve_id(manager.resolve_ids, zone, name='zone')
    return manager.dump_zone(zone_id)
