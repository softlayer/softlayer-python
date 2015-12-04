"""Import an image."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting


@click.command()
@click.argument('name')
@click.argument('uri')
@click.option('--note',
              default="",
              help="The note to be applied to the imported template")
@click.option('--os-code',
              default="",
              help="The referenceCode of the operating system software"
                   " description for the imported VHD")
@environment.pass_env
def cli(env, name, note, os_code, uri):
    """Import an image.

    The URI for an object storage object (.vhd/.iso file) of the format:
    swift://<objectStorageAccount>@<cluster>/<container>/<objectPath>
    """

    image_mgr = SoftLayer.ImageManager(env.client)
    result = image_mgr.import_image_from_uri(
        name=name,
        note=note,
        os_code=os_code,
        uri=uri,
    )

    if not result:
        raise exceptions.CLIAbort("Failed to import Image")

    table = formatting.KeyValueTable(['name', 'value'])
    table.align['name'] = 'r'
    table.align['value'] = 'l'
    table.add_row(['name', result['name']])
    table.add_row(['id', result['id']])
    table.add_row(['created', result['createDate']])
    table.add_row(['guid', result['globalIdentifier']])
    env.fout(table)
