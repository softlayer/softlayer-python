"""Delete a CDN domain mapping."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.argument('unique_id')
@environment.pass_env
def cli(env, unique_id):
    """Delete a CDN domain mapping."""

    manager = SoftLayer.CDNManager(env.client)

    cdn = manager.delete_cdn(unique_id)

    if cdn:
        env.fout("Cdn with uniqueId: {} was deleted.".format(unique_id))
