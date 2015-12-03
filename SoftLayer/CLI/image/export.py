"""Export an image."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import helpers


@click.command()
@click.argument('identifier')
@click.argument('uri')
@environment.pass_env
def cli(env, identifier, uri):
    """Export an image to object storage.

    The URI for an object storage object (.vhd/.iso file) of the format:
    swift://<objectStorageAccount>@<cluster>/<container>/<objectPath>
    """

    image_mgr = SoftLayer.ImageManager(env.client)
    image_id = helpers.resolve_id(image_mgr.resolve_ids, identifier, 'image')
    result = image_mgr.export_image_to_uri(image_id, uri)

    if not result:
        raise exceptions.CLIAbort("Failed to export Image")
