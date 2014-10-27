"""Delete zone."""
# :license: MIT, see LICENSE for more details.

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers

import click


@click.command()
@click.argument('zone')
@environment.pass_env
def cli(env, zone):
    """Delete zone."""

    manager = SoftLayer.DNSManager(env.client)
    zone_id = helpers.resolve_id(manager.resolve_ids, zone, name='zone')

    if env.skip_confirmations or formatting.no_going_back(zone):
        manager.delete_zone(zone_id)
    else:
        raise exceptions.CLIAbort("Aborted.")
