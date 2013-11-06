"""
usage: sl image [<command>] [<args>...] [options]

Manage compute and flex images

The available commands are:
  list  List images
"""
# :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
# :license: MIT, see LICENSE for more details.

from SoftLayer.CLI import CLIRunnable, Table
from SoftLayer.CLI.helpers import blank


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
        account = self.client['Account']

        neither = not any([args['--private'], args['--public']])

        results = []
        if args['--private'] or neither:
            account = self.client['Account']
            mask = 'id,accountId,name,globalIdentifier,blockDevices,parentId'
            r = account.getPrivateBlockDeviceTemplateGroups(mask=mask)

            results.append(r)

        if args['--public'] or neither:
            vgbd = self.client['Virtual_Guest_Block_Device_Template_Group']
            r = vgbd.getPublicImages()

            results.append(r)

        t = Table(['id', 'account', 'type', 'name', 'guid', ])
        t.sortby = 'name'

        for result in results:
            images = filter(lambda x: x['parentId'] == '', result)
            for image in images:
                t.add_row([
                    image['id'],
                    image.get('accountId', blank()),
                    image.get('type', blank()),
                    image['name'].strip(),
                    image.get('globalIdentifier', blank()),
                ])

        return t
