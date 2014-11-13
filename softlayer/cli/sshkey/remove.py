"""Permanently removes an SSH key."""
# :license: MIT, see LICENSE for more details.

import softlayer
from softlayer.cli import environment
from softlayer.cli import exceptions
from softlayer.cli import formatting
from softlayer.cli import helpers

import click


@click.command()
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """Permanently removes an SSH key."""
    mgr = softlayer.SshKeyManager(env.client)

    key_id = helpers.resolve_id(mgr.resolve_ids, identifier, 'SshKey')
    if env.skip_confirmations or formatting.no_going_back(key_id):
        mgr.delete_key(key_id)
    else:
        raise exceptions.CLIAbort('Aborted')
