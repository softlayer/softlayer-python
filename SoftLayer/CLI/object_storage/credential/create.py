"""Create credentials for an IBM Cloud Object Storage Account."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting


@click.command()
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """Create credentials for an IBM Cloud Object Storage Account"""

    mgr = SoftLayer.ObjectStorageManager(env.client)
    credential = mgr.create_credential(identifier)
    table = formatting.Table(['id', 'password', 'username', 'type_name'])
    table.sortby = 'id'
    table.add_row([
        credential['id'],
        credential['password'],
        credential['username'],
        credential['type']['name']
    ])

    env.fout(table)
