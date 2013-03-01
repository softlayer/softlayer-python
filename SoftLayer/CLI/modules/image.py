"""
usage: sl image [<command>] [<args>...] [options]

Manage compute and flex images

The available commands are:
  list  List active vlans with firewalls
"""

from SoftLayer.CLI import CLIRunnable, Table


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

        result = []
        if args['--private'] or neither:
            account = client['Account']
            private = "privateBlockDeviceTemplateGroups"
            mask = (
                private +
                '[id,accountId,name,globalIdentifier,blockDevices,parentId]')

            result += account.getObject(mask=mask)[private]

        if args['--public'] or neither:
            vgbd = client['Virtual_Guest_Block_Device_Template_Group']
            result += vgbd.getPublicImages()

        t = Table(['id', 'account', 'type', 'name', 'guid', ])
        t.sortby = 'name'

        images = filter(lambda x: x['parentId'] == '', result)
        for image in images:
            t.add_row([
                image['id'],
                image.get('accountId', '-'),
                image.get('type', '-'),
                image['name'].strip(),
                image.get('globalIdentifier', '-'),
            ])

        return t
