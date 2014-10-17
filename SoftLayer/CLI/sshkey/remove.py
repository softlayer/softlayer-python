"""Permanently removes an SSH key"""
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
    """Permanently removes an SSH key"""
    mgr = SoftLayer.SshKeyManager(env.client)

    key_id = helpers.resolve_id(mgr.resolve_ids, identifier, 'SshKey')
    if env.skip_confirmations or formatting.no_going_back(key_id):
        mgr.delete_key(key_id)
    else:
        raise exceptions.CLIAbort('Aborted')
