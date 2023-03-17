"""Share an image template with another account."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import helpers


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.argument('identifier')
@click.option('--account-id', help='Account Id for another account to share image template', required=True)
@environment.pass_env
def cli(env, identifier, account_id):
    """Share an image template with another account."""

    image_mgr = SoftLayer.ImageManager(env.client)
    image_id = helpers.resolve_id(image_mgr.resolve_ids, identifier, 'image')
    shared_image = image_mgr.share_image(image_id, account_id)

    if shared_image:
        env.fout("Image template {} was shared to account {}.".format(identifier, account_id))
