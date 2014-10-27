"""Create an origin pull mapping."""
# :license: MIT, see LICENSE for more details.

import SoftLayer
from SoftLayer.CLI import environment

import click
# pylint: disable=redefined-builtin


@click.command()
@click.argument('account_id')
@click.argument('content_url')
@click.option('--type',
              help='The media type for this mapping (http, flash, wm, ...)',
              default='http')
@click.option('--cname',
              help='An optional CNAME to attach to the mapping')
@environment.pass_env
def cli(env, account_id, content_url, type, cname):
    """Create an origin pull mapping."""

    manager = SoftLayer.CDNManager(env.client)
    manager.add_origin(account_id, type, content_url, cname)
