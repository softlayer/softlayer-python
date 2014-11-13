"""Reload operating system on a server."""
# :license: MIT, see LICENSE for more details.

import softlayer
from softlayer.cli import environment
from softlayer.cli import exceptions
from softlayer.cli import formatting
from softlayer.cli import helpers

import click


@click.command()
@click.argument('identifier')
@click.option('--postinstall', '-i', help="SSH keys to add to the root user")
@helpers.multi_option('--key', '-k',
                      help="""Post-install script to download
 (Only HTTPS executes, HTTP leaves file in /root)""")
@environment.pass_env
def cli(env, identifier, postinstall, key):
    """Reload operating system on a server."""

    hardware = softlayer.HardwareManager(env.client)
    hardware_id = helpers.resolve_id(hardware.resolve_ids,
                                     identifier,
                                     'hardware')
    key_list = []
    if key:
        for single_key in key:
            resolver = softlayer.SshKeyManager(env.client).resolve_ids
            key_id = helpers.resolve_id(resolver, single_key, 'SshKey')
            key_list.append(key_id)
    if env.skip_confirmations or formatting.no_going_back(hardware_id):
        hardware.reload(hardware_id, postinstall, key_list)
    else:
        raise exceptions.CLIAbort('Aborted')
