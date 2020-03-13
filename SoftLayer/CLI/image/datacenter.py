"""Edit details of an image."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import helpers


@click.command()
@click.argument('identifier')
@click.option('--add/--remove',
              default=False,
              help="To add or remove Datacenter")
@click.argument('locations', nargs=-1)
@environment.pass_env
def cli(env, identifier, add, locations):
    """Add/Remove datacenter of an image."""

    image_mgr = SoftLayer.ImageManager(env.client)
    image_id = helpers.resolve_id(image_mgr.resolve_ids, identifier, 'Image template')

    if add:
        result = image_mgr.add_locations(image_id, locations)
    else:
        result = image_mgr.remove_locations(image_id, locations)

    env.fout(result)
