"""Prints out an SSH key to the screen."""
# :license: MIT, see LICENSE for more details.
from os import path

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.argument('identifier')
@click.option('--out-file', '-f',
              type=click.Path(exists=True, writable=True),
              help="The public SSH key will be written to this file")
@environment.pass_env
def cli(env, identifier, out_file):
    """Prints out an SSH key to the screen."""

    mgr = SoftLayer.SshKeyManager(env.client)

    key_id = helpers.resolve_id(mgr.resolve_ids, identifier, 'SshKey')

    key = mgr.get_key(key_id)

    if out_file:
        with open(path.expanduser(out_file), 'w', encoding="utf-8") as pub_file:
            pub_file.write(key['key'])

    table = formatting.KeyValueTable(['name', 'value'])
    table.add_row(['id', key['id']])
    table.add_row(['label', key.get('label')])
    table.add_row(['notes', key.get('notes', '-')])
    env.fout(table)
