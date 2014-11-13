"""Delete an image."""
# :license: MIT, see LICENSE for more details.

import softlayer
from softlayer.cli import environment
from softlayer.cli import helpers

import click


@click.command()
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """Delete an image."""

    image_mgr = softlayer.ImageManager(env.client)
    image_id = helpers.resolve_id(image_mgr.resolve_ids, identifier, 'image')

    image_mgr.delete_image(image_id)
