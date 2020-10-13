""" Credential limits for this IBM Cloud Object Storage account."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting


@click.command()
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """Credential limits for this IBM Cloud Object Storage account."""

    mgr = SoftLayer.ObjectStorageManager(env.client)
    credential_limit = mgr.limit_credential(identifier)
    table = formatting.Table(['limit'])
    table.add_row([
        credential_limit,
    ])

    env.fout(table)
