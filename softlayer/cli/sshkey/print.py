"""Prints out an SSH key to the screen."""
# :license: MIT, see LICENSE for more details.
from os import path

import softlayer
from softlayer.cli import environment
from softlayer.cli import formatting
from softlayer.cli import helpers

import click


@click.command()
@click.argument('identifier')
@click.option('--out-file', '-f',
              type=click.Path(exists=True, writable=True),
              help="The public SSH key will be written to this file")
@environment.pass_env
def cli(env, identifier, out_file):
    """Prints out an SSH key to the screen."""

    mgr = softlayer.SshKeyManager(env.client)

    key_id = helpers.resolve_id(mgr.resolve_ids, identifier, 'SshKey')

    key = mgr.get_key(key_id)

    if out_file:
        with open(path.expanduser(out_file), 'w') as pub_file:
            pub_file.write(key['key'])

    table = formatting.KeyValueTable(['Name', 'Value'])
    table.add_row(['id', key['id']])
    table.add_row(['label', key.get('label')])
    table.add_row(['notes', key.get('notes', '-')])
    return table
