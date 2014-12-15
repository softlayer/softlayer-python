"""Edit details of an image."""
# :license: MIT, see LICENSE for more details.

import softlayer
from softlayer.cli import environment
from softlayer.cli import exceptions
from softlayer.cli import helpers

import click


@click.command()
@click.argument('identifier')
@click.option('--name', help="Name of the image")
@click.option('--note', help="Additional note for the image")
@click.option('--tag', help="Tags for the image")
@environment.pass_env
def cli(env, identifier, name, note, tag):
    """Edit details of an image."""

    image_mgr = softlayer.ImageManager(env.client)
    data = {}
    if name:
        data['name'] = name
    if note:
        data['note'] = note
    if tag:
        data['tag'] = tag
    image_id = helpers.resolve_id(image_mgr.resolve_ids, identifier, 'image')
    if not image_mgr.edit(image_id, **data):
        raise exceptions.CLIAbort("Failed to Edit Image")
