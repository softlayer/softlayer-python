"""Reload the OS on a virtual server."""
# :license: MIT, see LICENSE for more details.

import softlayer
from softlayer.cli import environment
from softlayer.cli import exceptions
from softlayer.cli import formatting
from softlayer.cli import helpers

import click


@click.command()
@click.argument('identifier')
@click.option('--postinstall', '-i', help="Post-install script to download")
@helpers.multi_option('--key', '-k',
                      help="SSH keys to add to the root user")
@environment.pass_env
def cli(env, identifier, postinstall, key):
    """Reload operating system on a virtual server."""

    vsi = softlayer.VSManager(env.client)
    vs_id = helpers.resolve_id(vsi.resolve_ids, identifier, 'VS')
    keys = []
    if key:
        for single_key in key:
            resolver = softlayer.SshKeyManager(env.client).resolve_ids
            key_id = helpers.resolve_id(resolver, single_key, 'SshKey')
            keys.append(key_id)
    if env.skip_confirmations or formatting.no_going_back(vs_id):
        vsi.reload_instance(vs_id, postinstall, keys)
    else:
        raise exceptions.CLIAbort('Aborted')
