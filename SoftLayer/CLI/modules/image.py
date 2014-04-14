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

from SoftLayer import ImageManager
from SoftLayer.CLI import CLIRunnable, Table, KeyValueTable, blank, resolve_id
from SoftLayer.CLI.helpers import CLIAbort


class ListImages(CLIRunnable):
    """
usage: sl image list [--public | --private] [options]

List images

Options:
  --private  Display only private images
  --public   Display only public images
"""
    action = 'list'

    def execute(self, args):
        image_mgr = ImageManager(self.client)

        neither = not any([args['--private'], args['--public']])
        mask = 'id,accountId,name,globalIdentifier,blockDevices,parentId'

        images = []
        if args['--private'] or neither:
            for image in image_mgr.list_private_images(mask=mask):
                image['visibility'] = 'private'
                images.append(image)

        if args['--public'] or neither:
            for image in image_mgr.list_public_images(mask=mask):
                image['visibility'] = 'public'
                images.append(image)

        table = Table(['id',
                       'account',
                       'visibility',
                       'name',
                       'global_identifier'])

        images = [image for image in images if image['parentId'] == '']
        for image in images:
            table.add_row([
                image['id'],
                image.get('accountId', blank()),
                image['visibility'],
                image['name'].strip(),
                image.get('globalIdentifier', blank()),
            ])

        return table


class DetailImage(CLIRunnable):
    """
usage: sl image detail <identifier> [options]

Get details for an image
"""
    action = 'detail'

    def execute(self, args):
        image_mgr = ImageManager(self.client)
        image_id = resolve_id(image_mgr.resolve_ids,
                              args.get('<identifier>'),
                              'image')

        image = image_mgr.get_image(image_id)

        table = KeyValueTable(['Name', 'Value'])
        table.align['Name'] = 'r'
        table.align['Value'] = 'l'

        table.add_row(['id', image['id']])
        table.add_row(['account', image.get('accountId', blank())])
        table.add_row(['name', image['name'].strip()])
        table.add_row(['global_identifier',
                       image.get('globalIdentifier', blank())])

        return table


class DeleteImage(CLIRunnable):
    """
usage: sl image delete <identifier> [options]

Get details for an image
"""
    action = 'delete'

    def execute(self, args):
        image_mgr = ImageManager(self.client)
        image_id = resolve_id(image_mgr.resolve_ids,
                              args.get('<identifier>'),
                              'image')

        image_mgr.delete_image(image_id)


class EditImage(CLIRunnable):
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
        image_mgr = ImageManager(self.client)
        data = {}
        if args.get('--name'):
            data['name'] = args.get('--name')
        if args.get('--note'):
            data['note'] = args.get('--note')
        if args.get('--tag'):
            data['tag'] = args.get('--tag')
        image_id = resolve_id(image_mgr.resolve_ids,
                              args.get('<identifier>'), 'image')
        if not image_mgr.edit(image_id, **data):
            raise CLIAbort("Failed to Edit Image")
