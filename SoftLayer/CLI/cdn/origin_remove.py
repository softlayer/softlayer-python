"""Remove an origin pull mapping."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment


@click.command()
@click.argument('account_id')
@click.argument('origin_id')
@environment.pass_env
def cli(env, account_id, origin_id):
    """Remove an origin pull mapping."""

    manager = SoftLayer.CDNManager(env.client)
    manager.remove_origin(account_id, origin_id)
