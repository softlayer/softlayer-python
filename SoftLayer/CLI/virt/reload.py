"""Reload the OS on a virtual server."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers


@click.command()
@click.argument('identifier')
@click.option('--postinstall', '-i', help="Post-install script to download")
@click.option(
    '--image',
    help="""Image ID. The default is to use the current operating system.
See: 'slcli image list' for reference""")
@helpers.multi_option('--key', '-k',
                      help="SSH keys to add to the root user")
@environment.pass_env
def cli(env, identifier, postinstall, key, image):
    """Reload operating system on a virtual server."""

    vsi = SoftLayer.VSManager(env.client)
    vs_id = helpers.resolve_id(vsi.resolve_ids, identifier, 'VS')
    keys = []
    if key:
        for single_key in key:
            resolver = SoftLayer.SshKeyManager(env.client).resolve_ids
            key_id = helpers.resolve_id(resolver, single_key, 'SshKey')
            keys.append(key_id)
    if not (env.skip_confirmations or formatting.no_going_back(vs_id)):
        raise exceptions.CLIAbort('Aborted')

    vsi.reload_instance(vs_id,
                        post_uri=postinstall,
                        ssh_keys=keys,
                        image_id=image)
