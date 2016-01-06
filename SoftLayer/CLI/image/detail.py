"""Get details for an image."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers
from SoftLayer.CLI import image as image_mod
from SoftLayer import utils


@click.command()
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """Get details for an image."""

    image_mgr = SoftLayer.ImageManager(env.client)
    image_id = helpers.resolve_id(image_mgr.resolve_ids, identifier, 'image')

    image = image_mgr.get_image(image_id, mask=image_mod.DETAIL_MASK)
    disk_space = 0
    datacenters = []
    for child in image.get('children'):
        disk_space = int(child.get('blockDevicesDiskSpaceTotal', 0))
        if child.get('datacenter'):
            datacenters.append(utils.lookup(child, 'datacenter', 'name'))

    table = formatting.KeyValueTable(['name', 'value'])
    table.align['name'] = 'r'
    table.align['value'] = 'l'

    table.add_row(['id', image['id']])
    table.add_row(['global_identifier',
                   image.get('globalIdentifier', formatting.blank())])
    table.add_row(['name', image['name'].strip()])
    table.add_row(['status', formatting.FormattedItem(
        utils.lookup(image, 'status', 'keyname'),
        utils.lookup(image, 'status', 'name'),
    )])
    table.add_row([
        'active_transaction',
        formatting.transaction_status(image.get('transaction')),
    ])
    table.add_row(['account', image.get('accountId', formatting.blank())])
    table.add_row(['visibility',
                   image_mod.PUBLIC_TYPE if image['publicFlag']
                   else image_mod.PRIVATE_TYPE])
    table.add_row(['type',
                   formatting.FormattedItem(
                       utils.lookup(image, 'imageType', 'keyName'),
                       utils.lookup(image, 'imageType', 'name'),
                   )])
    table.add_row(['flex', image.get('flexImageFlag')])
    table.add_row(['note', image.get('note')])
    table.add_row(['created', image.get('createDate')])
    table.add_row(['disk_space', formatting.b_to_gb(disk_space)])
    table.add_row(['datacenters', formatting.listing(sorted(datacenters),
                                                     separator=',')])

    env.fout(table)
