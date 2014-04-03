"""
usage: sl image [<command>] [<args>...] [options]

Manage compute images

The available commands are:
  delete  Delete an image
  detail  Output details about an image
  list    List images
"""
# :license: MIT, see LICENSE for more details.

from SoftLayer import ImageManager
from SoftLayer.utils import converter
from SoftLayer.CLI import CLIRunnable, Table, KeyValueTable, blank, resolve_id


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
        data = self._parmateter_parsing(image)

        table = KeyValueTable(['Name', 'Value'])
        table.align['Name'] = 'r'
        table.align['Value'] = 'l'

        table.add_row(['id', image['id']])
        table.add_row(['account', image.get('accountId', blank())])
        table.add_row(['name', image['name'].strip()])
        table.add_row(['global_identifier',
                       image.get('globalIdentifier', blank())])
        table.add_row(['note', data.get('note', blank())])
        table.add_row(['tag', data.get('tag', blank())])
        table.add_row(['datacenter', data.get('location', blank())])
        table.add_row(['status', data.get('status', blank())])
        table.add_row(['disk_utilized', data.get('size_value', blank())])
        table.add_row(['disk_capacity', data.get('capacity_value', blank())])

        return table

    def _parmateter_parsing(self, image):
        """
        Parsing the data to get the required information
        param image: contains image related data
        """
        data = {}
        data['note'] = image.get('note')
        data['tag'] = []
        for i in range(len(image['tagReferences'])):
            data['tag'].append(image['tagReferences'][i]['tag']['name'])
        data['status'] = image['status']['name']
        data['location'] = ""
        for i in range(len(image['children'])):
            data['location'] = data['location'] + "" + \
                str((image['children'][i]['datacenter']['longName'])) + ", "
        data['location'] = data['location'][0:-2]
        totalblockdevices = image['children'][0]['blockDevices']
        blockdevices_length = len(totalblockdevices)
        capacity = [[] for i in range(blockdevices_length)]
        capacity_unit = list(capacity)
        size_on_disk = list(capacity)
        size_on_disk_unit = list(capacity)
        for i in range(blockdevices_length):
            if totalblockdevices[i]['diskImage']['type']['name'] == 'Swap':
                continue
            capacity[i] = totalblockdevices[i]['diskImage']['capacity']
            capacity_unit[i] = totalblockdevices[i]['diskImage']['units']
            size_on_disk[i] = float(totalblockdevices[i]['diskSpace'])
            size_on_disk_unit[i] = totalblockdevices[i]['units']
            size_on_disk[i] = converter(size_on_disk[i])
        if [] in capacity:
            capacity.remove([])
            capacity_unit.remove([])
            size_on_disk.remove([])
            size_on_disk_unit.remove([])
        data['size_value'] = ""
        data['capacity_value'] = ""
        for i in range(len(capacity)):
            data['size_value'] = data['size_value'] + str(size_on_disk[i]) + \
                "    "
            data['capacity_value'] = data['capacity_value'] + \
                str(capacity[i]) + str(capacity_unit[i]) + "      "
        return data


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
