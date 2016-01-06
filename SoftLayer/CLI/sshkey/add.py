"""Add a new SSH key."""
# :license: MIT, see LICENSE for more details.
from os import path

import click

import SoftLayer
from SoftLayer.CLI import environment


@click.command()
@click.argument('label')
@click.option('--in-file', '-f',
              type=click.Path(exists=True),
              help="The id_rsa.pub file to import for this key")
@click.option('--key', '-k', help="The actual SSH key")
@click.option('--note', help="Extra note that will be associated with key")
@environment.pass_env
def cli(env, label, in_file, key, note):
    """Add a new SSH key."""

    if key:
        key_text = key
    else:
        key_file = open(path.expanduser(in_file), 'rU')
        key_text = key_file.read().strip()
        key_file.close()

    mgr = SoftLayer.SshKeyManager(env.client)
    result = mgr.add_key(key_text, label, note)

    env.fout("SSH key added: %s" % result.get('fingerprint'))
