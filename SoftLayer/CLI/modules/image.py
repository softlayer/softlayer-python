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
        data = self.parmateter_parsing(image)
        table = KeyValueTable(['Name', 'Value'])
        table.align['Name'] = 'r'
        table.align['Value'] = 'l'

        table.add_row(['id', image['id']])
        table.add_row(['account', image.get('accountId', blank())])
        table.add_row(['name', image['name'].strip()])
        table.add_row(['global_identifier',
                       image.get('globalIdentifier', blank())])

        return table

    def parmateter_parsing(self, image):
        data = {}
        data['note'] = image.get('note')
        data['tag'] = []
        for i in range(len(image['tagReferences'])):
            data['tag'].append(image['tagReferences'][i]['tag']['name'])
        data['status'] = image['status']['name']
        import pdb'pdb.set_trace() 
        data['capacity'] = [[] for i in range(len(image['children'][0]['blockDevices']))]
        data['capacity_unit'] = [[] for i in range(len(image['children'][0]['blockDevices']))]
        data['size_on_disk'] = [[] for i in range(len(image['children'][0]['blockDevices']))]
        data['size_on_disk_unit'] = [[] for i in range(len(image['children'][0]['blockDevices']))]
        for i in range(len(image['children'][0]['blockDevices']))]:
            if i ==1:
                continue 
            data['capacity'][i] = image['children'][0]['blockDevices'][
                i]['diskImage']['capacity']
            data['capacity_unit'][i] = image['children'][0]['blockDevices'][
                i]['diskImage']['units']
            data['size_on_disk'][i] = float(image['children'][
                i]['blockDevices'][0]['diskSpace'])
            data['size_on_disk_unit'][i] = image['children'][0]['blockDevices'][
                i]['units']
            while data['size_on_disk'][i] >= 1:
                if (data['size_on_disk'][i]/1024 > 1):
                    data['size_on_disk'][i] = data['size_on_disk'][i]/1024
                    if data['size_on_disk_unit'][i] == 'B':
                        data['size_on_disk_unit'][i] = 'KB'
                    elif data['size_on_disk_unit'][i] == 'KB':
                        data['size_on_disk_unit'][i] = 'MB'
                    elif data['size_on_disk_unit'][i] == 'MB':
                        data['size_on_disk_unit'][i] = 'GB'
                    elif data['size_on_disk_unit'][i] == 'GB':
                        data['size_on_disk_unit'][i] = 'TB'
                else:
                    break
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
