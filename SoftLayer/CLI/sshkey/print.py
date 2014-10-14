"""Prints out an SSH key to the screen"""
# :license: MIT, see LICENSE for more details.
from os import path

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers

import click


@click.command()
@click.argument('identifier')
@click.option('--file', '-f',
              type=click.Path(exists=True, writable=True),
              help="The public SSH key will be written to this file")
@environment.pass_env
def cli(env, identifier, file):
    """Prints out an SSH key to the screen"""

    mgr = SoftLayer.SshKeyManager(env.client)

    key_id = helpers.resolve_id(mgr.resolve_ids, identifier, 'SshKey')

    key = mgr.get_key(key_id)

    if file:
        with open(path.expanduser(file), 'w') as pub_file:
            pub_file.write(key['key'])

    table = formatting.KeyValueTable(['Name', 'Value'])
    table.add_row(['id', key['id']])
    table.add_row(['label', key.get('label')])
    table.add_row(['notes', key.get('notes', '-')])
    return table
