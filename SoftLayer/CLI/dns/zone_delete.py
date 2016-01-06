"""Delete zone."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers


@click.command()
@click.argument('zone')
@environment.pass_env
def cli(env, zone):
    """Delete zone."""

    manager = SoftLayer.DNSManager(env.client)
    zone_id = helpers.resolve_id(manager.resolve_ids, zone, name='zone')

    if not (env.skip_confirmations or formatting.no_going_back(zone)):
        raise exceptions.CLIAbort("Aborted.")

    manager.delete_zone(zone_id)
