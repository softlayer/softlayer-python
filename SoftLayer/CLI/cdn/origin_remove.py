"""Remove an origin pull mapping."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment


@click.command()
@click.argument('unique_id')
@click.argument('origin_path')
@environment.pass_env
def cli(env, unique_id, origin_path):
    """Removes an origin path for an existing CDN mapping."""

    manager = SoftLayer.CDNManager(env.client)
    manager.remove_origin(unique_id, origin_path)

    click.secho("Origin with path %s has been deleted" % origin_path, fg='green')
