"""Delete the credential of an Object Storage Account."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import helpers


@click.command()
@click.argument('identifier')
@click.option('--credential_id', '-c', type=click.INT,
              help="This is the credential id associated with the volume")
@environment.pass_env
def cli(env, identifier, credential_id):
    """Delete the credential of an Object Storage Account."""

    mgr = SoftLayer.ObjectStorageManager(env.client)
    storage_id = helpers.resolve_id(mgr.resolve_ids, identifier, 'Object Storage')
    credential = mgr.delete_credential(storage_id, credential_id=credential_id)

    env.fout(credential)
