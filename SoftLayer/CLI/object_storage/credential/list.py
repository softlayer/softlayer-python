"""Retrieve credentials used for generating an AWS signature. Max of 2."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting


@click.command()
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """Retrieve credentials used for generating an AWS signature. Max of 2."""

    mgr = SoftLayer.ObjectStorageManager(env.client)
    credential_list = mgr.list_credential(identifier)
    table = formatting.Table(['id', 'password', 'username', 'type_name'])

    for credential in credential_list:
        table.add_row([
            credential['id'],
            credential['password'],
            credential['username'],
            credential['type']['name']
        ])

    env.fout(table)
