"""Edits an SSH key."""
# :license: MIT, see LICENSE for more details.

import softlayer
from softlayer.cli import environment
from softlayer.cli import exceptions
from softlayer.cli import helpers

import click


@click.command()
@click.argument('identifier')
@click.option('--label', '-k', help="The new label for the key")
@click.option('--note', help="New notes for the key")
@environment.pass_env
def cli(env, identifier, label, note):
    """Edits an SSH key."""

    mgr = softlayer.SshKeyManager(env.client)

    key_id = helpers.resolve_id(mgr.resolve_ids, identifier, 'SshKey')

    if not mgr.edit_key(key_id, label=label, notes=note):
        raise exceptions.CLIAbort('Failed to edit SSH key')
