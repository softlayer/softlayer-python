#!/usr/bin/env python
"""Manage, delete, order Compute instances"""

from SoftLayer.CCI import CCIManager
from SoftLayer.CLI import CLIRunnable, Table, no_going_back, confirm
from argparse import FileType


class ListCCIs(CLIRunnable):
    """ List all CCI's on the account"""
    action = 'list'

    @staticmethod
    def add_additional_args(parser):
        group = parser.add_mutually_exclusive_group()
        group.add_argument(
            '--hourly',
            help='List only hourly CCI\'s',
            action='store_true', default=False)
        group.add_argument(
            '--monthly',
            help='List only monthly CCI\'s',
            action='store_true', default=False)

        parser.add_argument(
            '--sortby',
            help="Sort table",
            choices=['id', 'datacenter', 'host', 'cores', 'memory',
                     'primary_ip', 'backend_ip'],
            default='host')

    @staticmethod
    def execute(client, args):
        cci = CCIManager(client)

        guests = cci.list_instances(hourly=args.hourly, monthly=args.monthly)

        t = Table([
            'id', 'datacenter', 'host',
            'cores', 'memory', 'primary_ip',
            'backend_ip', 'provisioning',
        ])
        t.sortby = args.sortby

        for guest in guests:
            t.add_row([
                guest['id'],
                guest.get('datacenter', {}).get('name', 'unknown'),
                guest['fullyQualifiedDomainName'],
                guest['maxCpu'],
                guest['maxMemory'],
                guest.get('primaryIpAddress', '???'),
                guest.get('primaryBackendIpAddress', '???'),
                guest.get('activeTransaction', {}).get(
                    'transactionStatus', {}).get('friendlyName', '')
            ])

        return t


class CCIDetails(CLIRunnable):

    action = 'detail'

    @staticmethod
    def add_additional_args(parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument(
            '--id',
            help='id of CCI')

        group.add_argument(
            '--name',
            help='Fully qualified domain name')

        group.add_argument(
            '--public-ip',
            help='public ip of CCI',
            dest='public_ip'
        )

        parser.add_argument(
            "--passwords",
            help='Show passwords (check over your shoulder!)',
            action='store_true', default=False)

        parser.add_argument(
            '--price',
            help='Show associated prices',
            action='store_true', default=False)

    @staticmethod
    def execute(client, args):
        cci = CCIManager(client)

        t = Table(['Name', 'Value'])
        t.align['Name'] = 'r'
        t.align['Value'] = 'l'

        output = [
            ("id", "{0[id]}",),
            ("hostname", "{0[fullyQualifiedDomainName]}",),
            ("status", "{0[status][name]}",),
            ("state", "{0[powerState][name]}",),
            ("datacenter", "{0[datacenter][name]}",),
            ("cores", "{0[maxCpu]}",),
            ("memory", "{0[maxMemory]}MB",),
            ("public_ip", "{0[primaryIpAddress]}",),
            ("private_ip", "{0[primaryBackendIpAddress]}",),
            ("os", "{0[operatingSystem][softwareLicense]"
                "[softwareDescription][name]} "),
        ]

        result = cci.get_instance(args.id)

        for o in output:
            t.add_row([o[0], o[1].format(result)])

        if args.price:
            t.add_row(['price rate', result['billingItem']['recurringFee']])

        if args.passwords:
            t2 = Table(['username', 'password'])
            t2.border = False
            t2.header = False
            t2.align['username'] = 'r'
            t2.align['password'] = 'l'
            for item in result['operatingSystem']['passwords']:
                t2.add_row([item['username'], item['password']])
            t.add_row(['users', t2])

        return t


class CreateOptionsCCI(CLIRunnable):
    """ Output available available options when creating a CCI """

    action = 'options'
    filters = ['all', 'datacenter', 'cpu', 'nic', 'disk', 'os', 'memory']

    @classmethod
    def add_additional_args(cls, parser):
        for f in cls.filters:
            parser.add_argument(
                '--%s' % f,
                help="show %s options" % f,
                dest='filters',
                default=[],
                action='append_const',
                const=f)

    @classmethod
    def execute(cls, client, args):
        cci = CCIManager(client)
        result = cci.get_create_options()
        show_all = False
        if len(args.filters) == 0 or 'all' in args.filters:
            show_all = True

        t = Table(['Name', 'Value'])
        t.align['Name'] = 'r'
        t.align['Value'] = 'l'

        if 'datacenter' in args.filters or show_all:
            datacenters = ','.join(
                dc['template']['datacenter']['name']
                for dc in result['datacenters'])
            t.add_row(['datacenter', datacenters])

        if 'cpu' in args.filters or show_all:
            standard_cpu = filter(
                lambda x: not x['template'].get(
                    'dedicatedAccountHostOnlyFlag', False),
                result['processors'])

            ded_cpu = filter(
                lambda x: x['template'].get(
                    'dedicatedAccountHostOnlyFlag', False),
                result['processors'])

            def cpus_row(c, name):
                cpus = []
                for x in c:
                    cpus.append(str(x['template']['startCpus']))

                t.add_row(['cpus (%s)' % name, ','.join(cpus)])

            cpus_row(ded_cpu, 'private')
            cpus_row(standard_cpu, 'standard')

        if 'memory' in args.filters or show_all:
            memory = [
                str(m['template']['maxMemory']) for m in result['memory']]
            t.add_row(['memory', ','.join(memory)])

        if 'os' in args.filters or show_all:
            os = [
                o['template']['operatingSystemReferenceCode'] for o in
                result['operatingSystems']]

            os = sorted(os)
            os_summary = set()

            for o in os:
                os_summary.add(o[0:o.find('_')])

            for s in sorted(os_summary):
                t.add_row(['os (%s)' % s, "\n".join(
                    sorted(filter(lambda x: x[0:len(s)] == s, os))
                )])

        if 'disk' in args.filters or show_all:
            local_disks = filter(
                lambda x: x['template'].get('localDiskFlag', False),
                result['blockDevices'])

            san_disks = filter(
                lambda x: not x['template'].get('localDiskFlag', False),
                result['blockDevices'])

            def block_rows(blocks, name):
                simple = {}
                for block in blocks:
                    b = block['template']['blockDevices'][0]
                    bid = b['device']
                    size = b['diskImage']['capacity']

                    if bid not in simple:
                        simple[bid] = []

                    simple[bid].append(str(size))

                for b in sorted(simple.keys()):
                    t.add_row([
                        '%s disk(%s)' % (name, b),
                        ','.join(simple[b])]
                    )

            block_rows(local_disks, 'local')
            block_rows(san_disks, 'san')

        if 'nic' in args.filters or show_all:
            speeds = []
            for x in result['networkComponents']:
                speed = x['template']['networkComponents'][0]['maxSpeed']
                speeds.append(str(speed))

            speeds = sorted(speeds)

            t.add_row(['nic', ','.join(speeds)])

        return t


class CreateCCI(CLIRunnable):
    """ Order and create a CCI
    (see `sl cci options` for choices)"""

    action = 'create'

    @staticmethod
    def add_additional_args(parser):
        # Required options
        parser.add_argument(
            '--hostname', '-H',
            help='Host portion of the FQDN',
            type=str,
            required=True,
            metavar='server1')

        parser.add_argument(
            '--domain', '-D',
            help='Domain portion of the FQDN',
            type=str,
            required=True,
            metavar='example.com')

        parser.add_argument(
            '--cpu', '-c',
            help='Number of CPU cores',
            type=int,
            required=True,
            metavar='#')

        parser.add_argument(
            '--memory', '-m',
            help='Memory in mebibytes (n * 1024)',
            type=str,
            required=True)

        install = parser.add_mutually_exclusive_group(required=True)
        install.add_argument(
            '--os', '-o',
            help='OS install code. Tip: you can also specify <OS>_LATEST',
            type=str)
        install.add_argument(
            '--image',
            help='Image GUID',
            type=str,
            metavar='GUID')

        billable = parser.add_mutually_exclusive_group(required=True)
        billable.add_argument(
            '--hourly',
            help='Hourly rate instance type',
            action='store_true')
        billable.add_argument(
            '--monthly',
            help='Monthly rate instance type',
            action='store_true')

        # Optional arguments
        parser.add_argument(
            '--datacenter', '--dc', '-d',
            help='datacenter shortname (sng01, dal05, ...). '
            'Note: Omitting this value defaults to the first '
            'available datacenter',
            type=str,
            default='')

        parser.add_argument(
            '--private',
            help='Allocate a private CCI',
            action='store_true',
            default=False)

        g = parser.add_mutually_exclusive_group()
        g.add_argument(
            '--userdata', '-u',
            help="user defined metadata string",
            type=str,
            default=None)
        g.add_argument(
            '--userfile', '-F',
            help="read userdata from file",
            type=FileType('r'))

        parser.add_argument(
            '--test', '--dryrun', '--dry-run',
            help='Do not create CCI, just get a quote',
            action='store_true',
            default=False)

    @staticmethod
    def execute(client, args):
        cci = CCIManager(client)

        data = {
            "hourly": args.hourly,
            "cpus": args.cpu,
            "domain": args.domain,
            "hostname": args.hostname,
            "private": args.private,
            "local_disk": True,
        }

        try:
            memory = int(args.memory)
            if memory < 1024:
                memory = memory * 1024
        except ValueError:
            unit = args.memory[-1]
            memory = int(args.memory[0:-1])
            if unit in ['G', 'g']:
                memory = memory * 1024
            if unit in ['T', 'r']:
                memory = memory * 1024 * 1024

        data["memory"] = memory

        if args.monthly:
            data["hourly"] = False

        if args.os:
            data["os_code"] = args.os

        if args.image:
            data["image_id"] = args.image

        if args.datacenter:
            data["datacenter"] = args.datacenter

        if args.userdata:
            data['userdata'] = args.userdata
        elif args.userfile:
            data['userdata'] = args.userfile.read()

        if args.test:
            result = cci.verify_create_instance(**data)
            print("Test: Success!")
        elif args.really or confirm(
                prompt_str="This action will incur charges on "
                "your account. Continue?", allow_empty=True):
            result = cci.create_instance(**data)
            print("Success!")

        return result


class CancelCCI(CLIRunnable):
    """ Cancel a running CCI """

    action = 'cancel'

    @staticmethod
    def add_additional_args(parser):
        parser.add_argument('id', help='The ID of the CCI to cancel')

    @staticmethod
    def execute(client, args):
        cci = CCIManager(client)
        if args.really or no_going_back(args.id):
            cci.cancel_instance(args.id)
        else:
            print "Aborted."
