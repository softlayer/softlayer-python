"""Add a new SSH key."""
# :license: MIT, see LICENSE for more details.
from os import path

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.argument('label')
@click.option('--in-file', '-f',
              type=click.Path(exists=True),
              help="The id_rsa.pub file to import for this key")
@click.option('--key', '-k', help="The actual SSH key")
@click.option('--note', help="Extra note that will be associated with key")
@environment.pass_env
def cli(env, label, in_file, key, note):
    """Add a new SSH key."""

    if in_file is None and key is None:
        raise exceptions.ArgumentError(
            'Either [-f | --in-file] or [-k | --key] arguments are required to add a key'
        )

    if in_file and key:
        raise exceptions.ArgumentError(
            '[-f | --in-file] is not allowed with [-k | --key]'
        )

    if key:
        key_text = key
    else:
        with open(path.expanduser(in_file), encoding="utf-8") as key_file:
            key_text = key_file.read().strip()
            key_file.close()

    mgr = SoftLayer.SshKeyManager(env.client)
    result = mgr.add_key(key_text, label, note)

    env.fout("SSH key added: %s" % result.get('fingerprint'))
