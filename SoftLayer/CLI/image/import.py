"""Import an image."""
# :license: MIT, see LICENSE for more details.

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting


import click


@click.command()
@click.argument('name')
@click.argument('uri')
@click.option('--note', default="",
              help="The note to be applied to the imported template")
@click.option('--osrefcode', default="",
              help="The referenceCode of the operating system software"
                   " description for the imported VHD")
@environment.pass_env
def cli(env, name, note, osrefcode, uri):
    """Import an image."""

    image_mgr = SoftLayer.ImageManager(env.client)
    data = {}
    output = []
    if name:
        data['name'] = name
    if note:
        data['note'] = note
    if osrefcode:
        data['operatingSystemReferenceCode'] = osrefcode
    if uri:
        data['uri'] = uri

    # not sure if u should validate here or not
    # if uri.endswith(".vhd") and osrefcode == "":
    #    raise exceptions.CLIAbort("Please specify osrefcode for .vhdImage")

    result = image_mgr.import_image_from_uri(data)

    if not result:
        raise exceptions.CLIAbort("Failed to import Image")

    table = formatting.KeyValueTable(['name', 'value'])
    table.align['name'] = 'r'
    table.align['value'] = 'l'
    table.add_row(['name', result['name']])
    table.add_row(['id', result['id']])
    table.add_row(['created', result['createDate']])
    table.add_row(['guid', result['globalIdentifier']])
    output.append(table)
    return output
