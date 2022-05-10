"""Edits an SSH key."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import helpers


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.argument('identifier')
@click.option('--label', '-k', help="The new label for the key")
@click.option('--note', help="New notes for the key")
@environment.pass_env
def cli(env, identifier, label, note):
    """Edits an SSH key."""

    mgr = SoftLayer.SshKeyManager(env.client)

    key_id = helpers.resolve_id(mgr.resolve_ids, identifier, 'SshKey')

    if not mgr.edit_key(key_id, label=label, notes=note):
        raise exceptions.CLIAbort('Failed to edit SSH key')
