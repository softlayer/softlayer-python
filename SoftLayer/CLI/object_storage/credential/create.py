"""Create credentials for an IBM Cloud Object Storage Account."""
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
    """Create credentials for an IBM Cloud Object Storage Account"""

    mgr = SoftLayer.ObjectStorageManager(env.client)
    storage_id = helpers.resolve_id(mgr.resolve_ids, identifier, 'Object Storage')
    credential = mgr.create_credential(storage_id)
    table = formatting.Table(['id', 'password', 'username', 'type_name'])
    table.sortby = 'id'
    table.add_row([
        credential.get('id'),
        credential.get('password'),
        credential.get('username'),
        credential.get('type', {}).get('name')
    ])

    env.fout(table)
