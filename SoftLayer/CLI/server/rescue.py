"""Reboot server into a rescue image"""
# :license: MIT, see LICENSE for more details.

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers

import click


@click.command()
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """Reboot server into a rescue image"""

    server = SoftLayer.HardwareManager(env.client)
    server_id = helpers.resolve_id(server.resolve_ids, identifier, 'hardware')

    if env.skip_confirmations or formatting.confirm(
            "This action will reboot this server. "
            "Continue?"):

        server.rescue(server_id)
    else:
        raise exceptions.CLIAbort('Aborted')
