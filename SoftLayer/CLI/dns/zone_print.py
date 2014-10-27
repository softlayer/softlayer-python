"""Print zone in BIND format."""
# :license: MIT, see LICENSE for more details.

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import helpers

import click


@click.command()
@click.argument('zone')
@environment.pass_env
def cli(env, zone):
    """Print zone in BIND format."""

    manager = SoftLayer.DNSManager(env.client)
    zone_id = helpers.resolve_id(manager.resolve_ids, zone, name='zone')
    return manager.dump_zone(zone_id)
