""" Credential limits for this IBM Cloud Object Storage account."""
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
    """Credential limits for this IBM Cloud Object Storage account."""

    mgr = SoftLayer.ObjectStorageManager(env.client)
    storage_id = helpers.resolve_id(mgr.resolve_ids, identifier, 'Object Storage')
    credential_limit = mgr.limit_credential(storage_id)
    table = formatting.Table(['limit'])
    table.add_row([
        credential_limit,
    ])

    env.fout(table)
