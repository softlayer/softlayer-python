"""Get details for an image."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers
from SoftLayer.CLI import image as image_mod
from SoftLayer import utils


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """Get details for an image."""

    image_mgr = SoftLayer.ImageManager(env.client)
    image_id = helpers.resolve_id(image_mgr.resolve_ids, identifier, 'image')
    image = image_mgr.get_image(image_id, mask=image_mod.DETAIL_MASK)

    children_images = image.get('children')
    total_size = utils.lookup(image, 'firstChild', 'blockDevicesDiskSpaceTotal') or 0

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
        formatting.listing(_get_transaction_groups(children_images), separator=','),
    ])
    table.add_row(['account', image.get('accountId', formatting.blank())])
    table.add_row(['created', image.get('createDate')])
    table.add_row(['total_size', formatting.b_to_gb(total_size)])
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
    table.add_row(['datacenters', _get_datacenter_table(children_images)])
    table.add_row(['virtual disks', _get_virtual_disks(children_images)])
    table.add_row(['share image', _get_share_image(image)])

    env.fout(table)


def _get_datacenter_table(children_images):
    """Returns image details as datacenter, size, and transaction within a formatting table.

      :param children_images: A list of images.
      """
    table_datacenter = formatting.Table(['DC', 'size', 'transaction'])
    for child in children_images:
        table_datacenter.add_row([
            utils.lookup(child, 'datacenter', 'name'),
            formatting.b_to_gb(child.get('blockDevicesDiskSpaceTotal', 0)),
            formatting.transaction_status(child.get('transaction'))
        ])

    return table_datacenter


def _get_transaction_groups(children_images):
    """Returns a Set of transaction groups.

      :param children_images: A list of images.
      """
    transactions = set()
    for child in children_images:
        transactions.add(utils.lookup(child, 'transaction', 'transactionGroup', 'name'))

    return transactions


def _get_virtual_disks(children_images):
    """Returns image details as datacenter, size, and transaction within a formatting table.

      :param children_images: A list of images.
      """

    table_virtual_disks = formatting.Table(['Device', 'capacity', 'size on disk'])

    if utils.lookup(children_images[0], 'blockDevices'):
        for block_devices in children_images[0]['blockDevices']:
            device_name = utils.lookup(block_devices, 'diskImage', 'name')
            software_references = utils.lookup(block_devices, 'diskImage', 'softwareReferences')
            if len(software_references) > 0:
                device_name = utils.lookup(software_references[0], 'softwareDescription', 'longDescription')

            size_on_disk = formatting.b_to_gb(block_devices.get('diskSpace', 0))
            if block_devices.get('diskSpace', 0) == 0:
                size_on_disk = 'N/A'

            capacity = str(utils.lookup(block_devices, 'diskImage', 'capacity')) + \
                ' ' + utils.lookup(block_devices, 'diskImage', 'units')

            table_virtual_disks.add_row([
                device_name,
                capacity,
                size_on_disk
            ])

    return table_virtual_disks


def _get_share_image(image):
    """Returns image details as datacenter, size, and transaction within a formatting table.

      :param image: Detail information about image.
      """
    table_share_account = formatting.Table(['Account', 'shared on'])
    if utils.lookup(image, 'accountReferences'):
        for account in image['accountReferences']:
            if account['accountId'] != image['accountId']:
                table_share_account.add_row([
                    utils.lookup(account, 'accountId'),
                    utils.lookup(account, 'createDate'),
                ])

    return table_share_account
