#!/usr/bin/env python
"""Manage, delete, order Compute instances"""

from SoftLayer.CLI import CLIRunnable, Table


class ListImages(CLIRunnable):
    """ List all images on the account"""
    action = 'list'

    @staticmethod
    def add_additional_args(parser):
        g = parser.add_mutually_exclusive_group()
        g.add_argument(
            '--private',
            help="Display only account owned images",
            default=False,
            action="store_true")
        g.add_argument(
            '--public',
            help="Display only public images",
            default=False,
            action="store_true")

    @staticmethod
    def execute(client, args):
        account = client['Account']

        neither = not any([args.private, args.public])

        result = []
        if args.private or neither:
            account = client['Account']
            private = "privateBlockDeviceTemplateGroups"
            mask = (
                private +
                '[id,accountId,name,globalIdentifier,blockDevices,parentId]')

            result += account.getObject(mask=mask)[private]

        if args.public or neither:
            vgbd = client['Virtual_Guest_Block_Device_Template_Group']
            result += vgbd.getPublicImages()

        t = Table([
            'id',
            'account',
            'name',
            'guid',
        ])
        t.sortby = 'name'

        images = filter(lambda x: x['parentId'] == '', result)
        for image in images:
            t.add_row([
                image['id'],
                image.get('accountId', '???'),
                image['name'],
                image.get('globalIdentifier', '???'),
            ])

        return t
