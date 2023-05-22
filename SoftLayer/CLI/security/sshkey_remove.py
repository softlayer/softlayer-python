"""Permanently removes an SSH key."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """Permanently removes an SSH key."""
    mgr = SoftLayer.SshKeyManager(env.client)

    key_id = helpers.resolve_id(mgr.resolve_ids, identifier, 'SshKey')
    if not (env.skip_confirmations or formatting.no_going_back(key_id)):
        raise exceptions.CLIAbort('Aborted')

    mgr.delete_key(key_id)
