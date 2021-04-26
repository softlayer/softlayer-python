"""Retrieve credentials used for generating an AWS signature. Max of 2."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers


@click.command()
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """Retrieve credentials used for generating an AWS signature. Max of 2."""

    mgr = SoftLayer.ObjectStorageManager(env.client)
    storage_id = helpers.resolve_id(mgr.resolve_ids, identifier, 'Object Storage')
    credential_list = mgr.list_credential(storage_id)

    table = formatting.Table(['id', 'password', 'username', 'type_name'])

    for credential in credential_list:
        table.add_row([
            credential.get('id'),
            credential.get('password'),
            credential.get('username'),
            credential.get('type', {}).get('name')
        ])

    env.fout(table)
