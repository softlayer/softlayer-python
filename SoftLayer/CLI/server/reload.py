"""Reload operating system on a server."""
# :license: MIT, see LICENSE for more details.

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers

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

    hardware = SoftLayer.HardwareManager(env.client)
    hardware_id = helpers.resolve_id(hardware.resolve_ids,
                                     identifier,
                                     'hardware')
    key_list = []
    if key:
        for single_key in key:
            resolver = SoftLayer.SshKeyManager(env.client).resolve_ids
            key_id = helpers.resolve_id(resolver, single_key, 'SshKey')
            key_list.append(key_id)
    if not (env.skip_confirmations or formatting.no_going_back(hardware_id)):
        raise exceptions.CLIAbort('Aborted')

    hardware.reload(hardware_id, postinstall, key_list)
