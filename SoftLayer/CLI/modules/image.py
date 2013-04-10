"""
usage: sl image [<command>] [<args>...] [options]

Manage compute and flex images

The available commands are:
  list  List active vlans with firewalls
"""
# :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
# :license: BSD, see LICENSE for more details.

from SoftLayer.CLI import CLIRunnable, Table
from SoftLayer.CLI.helpers import blank


class ListImages(CLIRunnable):
    """
usage: sl image list [--public | --private] [options]

List images on the account

Options:
  --public   Display only public images
  --private  Display only private images
"""
    action = 'list'

    @staticmethod
    def execute(client, args):
        account = client['Account']

        neither = not any([args['--private'], args['--public']])

        results = []
        if args['--private'] or neither:
            account = client['Account']
            mask = 'id,accountId,name,globalIdentifier,blockDevices,parentId'
            r = account.getPrivateBlockDeviceTemplateGroups(mask=mask)

            results.append(r)

        if args['--public'] or neither:
            vgbd = client['Virtual_Guest_Block_Device_Template_Group']
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
