"""Delete zone."""
# :license: MIT, see LICENSE for more details.

import softlayer
from softlayer.cli import environment
from softlayer.cli import exceptions
from softlayer.cli import formatting
from softlayer.cli import helpers

import click


@click.command()
@click.argument('zone')
@environment.pass_env
def cli(env, zone):
    """Delete zone."""

    manager = softlayer.DNSManager(env.client)
    zone_id = helpers.resolve_id(manager.resolve_ids, zone, name='zone')

    if env.skip_confirmations or formatting.no_going_back(zone):
        manager.delete_zone(zone_id)
    else:
        raise exceptions.CLIAbort("Aborted.")
