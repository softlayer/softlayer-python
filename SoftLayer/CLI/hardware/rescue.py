"""Reboot server into a rescue image."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers


@click.command()
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """Reboot server into a rescue image."""

    server = SoftLayer.HardwareManager(env.client)
    server_id = helpers.resolve_id(server.resolve_ids, identifier, 'hardware')

    if not (env.skip_confirmations or
            formatting.confirm("This action will reboot this server. "
                               "Continue?")):

        raise exceptions.CLIAbort('Aborted')

    server.rescue(server_id)
