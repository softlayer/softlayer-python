"""List images."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.CLI import image as image_mod
from SoftLayer import utils


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.option('--name', default=None, help='Filter on image name')
@click.option('--public/--private', is_flag=True, default=None,
              help='Display only public or private images')
@environment.pass_env
def cli(env, name, public):
    """List images."""

    image_mgr = SoftLayer.ImageManager(env.client)

    images = []
    if public in [False, None]:
        for image in image_mgr.list_private_images(name=name, mask=image_mod.MASK):
            images.append(image)

    if public in [True, None]:
        for image in image_mgr.list_public_images(name=name, mask=image_mod.MASK):
            images.append(image)

    table = formatting.Table(['Id', 'Name', 'Type', 'Visibility', 'Account', 'OS', 'Created', 'Notes'])
    table.align['OS'] = 'l'
    table.align['Notes'] = 'l'

    images = [image for image in images if not image['parentId']]
    for image in images:
        operative_system = '-'
        if image.get('children') and len(image.get('children')) != 0:
            if image.get('children')[0].get('blockDevices') and len(image.get('children')[0].get('blockDevices')) != 0:
                for block_device in image.get('children')[0].get('blockDevices'):
                    if block_device.get('diskImage').get('softwareReferences') and \
                            len(block_device.get('diskImage').get('softwareReferences')) != 0:
                        operative_system = block_device.get('diskImage').get('softwareReferences')[0].\
                            get('softwareDescription').get('longDescription')
        visibility = (image_mod.PUBLIC_TYPE if image['publicFlag'] else image_mod.PRIVATE_TYPE)
        table.add_row([
            image.get('id', formatting.blank()),
            formatting.FormattedItem(image['name'], click.wrap_text(image['name'], width=50)),
            formatting.FormattedItem(
                utils.lookup(image, 'imageType', 'keyName'),
                utils.lookup(image, 'imageType', 'name')),
            visibility,
            image.get('accountId', formatting.blank()),
            operative_system,
            utils.clean_time(image.get('createDate', formatting.blank())),
            image.get('note', formatting.blank()),
        ])

    env.fout(table)
