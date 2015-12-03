"""Purge cached files from all edge nodes."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment


@click.command()
@click.argument('account_id')
@click.argument('content_url', nargs=-1)
@environment.pass_env
def cli(env, account_id, content_url):
    """Purge cached files from all edge nodes."""

    manager = SoftLayer.CDNManager(env.client)
    manager.purge_content(account_id, content_url)
