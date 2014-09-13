"""
usage: sl image [<command>] [<args>...] [options]

Manage compute images

The available commands are:
  delete  Delete an image
  detail  Output details about an image
  list    List images
  edit    Edit an image
"""
# :license: MIT, see LICENSE for more details.

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers
from SoftLayer import utils

MASK = ('id,accountId,name,globalIdentifier,parentId,publicFlag,flexImageFlag,'
        'imageType')
DETAIL_MASK = MASK + (',children[id,blockDevicesDiskSpaceTotal,datacenter],'
                      'note,createDate,status')
PUBLIC_TYPE = formatting.FormattedItem('PUBLIC', 'Public')
PRIVATE_TYPE = formatting.FormattedItem('PRIVATE', 'Private')


class ListImages(environment.CLIRunnable):
    """
usage: sl image list [--public | --private] [options]

List images

Options:
  --private  Display only private images
  --public   Display only public images
"""
    action = 'list'

    def execute(self, args):
        image_mgr = SoftLayer.ImageManager(self.client)

        neither = not any([args['--private'], args['--public']])

        images = []
        if args['--private'] or neither:
            for image in image_mgr.list_private_images(mask=MASK):
                images.append(image)

        if args['--public'] or neither:
            for image in image_mgr.list_public_images(mask=MASK):
                images.append(image)

        table = formatting.Table(['id',
                                  'account',
                                  'name',
                                  'type',
                                  'visibility',
                                  'global_identifier'])

        images = [image for image in images if image['parentId'] == '']
        for image in images:

            table.add_row([
                image['id'],
                image.get('accountId', formatting.blank()),
                image['name'].strip(),
                formatting.FormattedItem(
                    utils.lookup(image, 'imageType', 'keyName'),
                    utils.lookup(image, 'imageType', 'name')),
                PUBLIC_TYPE if image['publicFlag'] else PRIVATE_TYPE,
                image.get('globalIdentifier', formatting.blank()),
            ])

        return table


class DetailImage(environment.CLIRunnable):
    """
usage: sl image detail <identifier> [options]

Get details for an image
"""
    action = 'detail'

    def execute(self, args):
        image_mgr = SoftLayer.ImageManager(self.client)
        image_id = helpers.resolve_id(image_mgr.resolve_ids,
                                      args.get('<identifier>'),
                                      'image')

        image = image_mgr.get_image(image_id, mask=DETAIL_MASK)
        disk_space = 0
        datacenters = []
        for child in image.get('children'):
            disk_space = int(child.get('blockDevicesDiskSpaceTotal', 0))
            if child.get('datacenter'):
                datacenters.append(utils.lookup(child, 'datacenter', 'name'))

        table = formatting.KeyValueTable(['Name', 'Value'])
        table.align['Name'] = 'r'
        table.align['Value'] = 'l'

        table.add_row(['id', image['id']])
        table.add_row(['global_identifier',
                       image.get('globalIdentifier', formatting.blank())])
        table.add_row(['name', image['name'].strip()])
        table.add_row(['status', formatting.FormattedItem(
            utils.lookup(image, 'status', 'keyname'),
            utils.lookup(image, 'status', 'name'),
        )])
        table.add_row(['account', image.get('accountId', formatting.blank())])
        table.add_row(['visibility',
                       PUBLIC_TYPE if image['publicFlag'] else PRIVATE_TYPE])
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

        return table


class DeleteImage(environment.CLIRunnable):
    """
usage: sl image delete <identifier> [options]

Get details for an image
"""
    action = 'delete'

    def execute(self, args):
        image_mgr = SoftLayer.ImageManager(self.client)
        image_id = helpers.resolve_id(image_mgr.resolve_ids,
                                      args.get('<identifier>'),
                                      'image')

        image_mgr.delete_image(image_id)


class EditImage(environment.CLIRunnable):
    """
usage: sl image edit <identifier> [--tag=Tag...] [options]

Edit Details for an image

Options:
    --name=Name     Name of the Image
    --note=Note     Note of the Image
    --tag=TAG...    Tags of the Image. Can be specified multiple times.

Note: Image to be edited must be private
"""
    action = 'edit'

    def execute(self, args):
        image_mgr = SoftLayer.ImageManager(self.client)
        data = {}
        if args.get('--name'):
            data['name'] = args.get('--name')
        if args.get('--note'):
            data['note'] = args.get('--note')
        if args.get('--tag'):
            data['tag'] = args.get('--tag')
        image_id = helpers.resolve_id(image_mgr.resolve_ids,
                                      args.get('<identifier>'), 'image')
        if not image_mgr.edit(image_id, **data):
            raise exceptions.CLIAbort("Failed to Edit Image")
