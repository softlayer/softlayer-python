"""List images."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.CLI import image as image_mod
from SoftLayer import utils


@click.command()
@click.option('--name', default=None, help='Filter on image name')
@click.option('--public/--private',
              is_flag=True,
              default=None,
              help='Display only public or private images')
@environment.pass_env
def cli(env, name, public):
    """List images."""

    image_mgr = SoftLayer.ImageManager(env.client)

    images = []
    if public in [False, None]:
        for image in image_mgr.list_private_images(name=name,
                                                   mask=image_mod.MASK):
            images.append(image)

    if public in [True, None]:
        for image in image_mgr.list_public_images(name=name,
                                                  mask=image_mod.MASK):
            images.append(image)

    table = formatting.Table(['id',
                              'name',
                              'type',
                              'visibility',
                              'account'])

    images = [image for image in images if image['parentId'] == '']
    for image in images:

        visibility = (image_mod.PUBLIC_TYPE if image['publicFlag']
                      else image_mod.PRIVATE_TYPE)
        table.add_row([
            image.get('id', formatting.blank()),
            formatting.FormattedItem(image['name'],
                                     click.wrap_text(image['name'], width=50)),
            formatting.FormattedItem(
                utils.lookup(image, 'imageType', 'keyName'),
                utils.lookup(image, 'imageType', 'name')),
            visibility,
            image.get('accountId', formatting.blank()),
        ])

    env.fout(table)
