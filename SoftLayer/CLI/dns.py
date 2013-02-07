#!/usr/bin/env python
"""Manages DNS"""

from SoftLayer.CLI import CLIRunnable, no_going_back, Table
from SoftLayer.DNS import DNSManager


def add_zone_arguments(parser):
    parser.add_argument('domain')


def add_record_arguments(parser):
    add_zone_arguments(parser)
    parser.add_argument('record')


class DumpZone(CLIRunnable):
    """ print zone in BIND format"""
    action = "print"

    @staticmethod
    def add_additional_args(parser):
        return add_zone_arguments(parser)

    @staticmethod
    def execute(client, args):
        manager = DNSManager(client)
        return manager.dump_zone(manager.get_zone(args.domain)['id'])


class CreateZone(CLIRunnable):
    """ create zone """
    action = 'create'

    @staticmethod
    def add_additional_args(parser):
        return add_zone_arguments(parser)

    @staticmethod
    def execute(client, args):
        manager = DNSManager(client)
        manager.create_zone(args.domain)
        print("Created zone:", args.domain)


class DeleteZone(CLIRunnable):
    """ delete zone"""
    action = 'delete'

    @staticmethod
    def add_additional_args(parser):
        return add_zone_arguments(parser)

    @staticmethod
    def execute(client, args):
        manager = DNSManager(client)
        if args.really or no_going_back(args.domain):
            manager.delete_zone(args.domain)
            print("Deleted zone:", args.domain)
        else:
            print("Aborted.")


class ListZones(CLIRunnable):
    """ list zones """
    action = 'list'

    @staticmethod
    def execute(client, args):
        manager = DNSManager(client)
        zones = manager.list_zones()
        t = Table([
            "id",
            "zone",
            "serial",
            "updated",
        ])
        t.align['serial'] = 'c'
        t.align['updated'] = 'c'

        for z in zones:
            t.add_row([
                z['id'],
                z['name'],
                z['serial'],
                z['updateDate'],
            ])

        return t


class AddRecord(CLIRunnable):
    """ add resource record"""
    action = 'add'

    @staticmethod
    def execute(client, args):
        manager = DNSManager(client)
        zone = manager.get_zone(args.domain)['id']
        manager.create_record(
            zone,
            args.record,
            args.type,
            args.data,
            ttl=args.ttl)

    @staticmethod
    def add_additional_args(parser):
        add_record_arguments(parser)
        parser.add_argument(
            'type',
            choices=['A', 'AAAA', 'CNAME', 'MX', 'NS',
                     'PTR', 'SPF', 'SRV', 'TXT'],
        )
        parser.add_argument('data')
        parser.add_argument('--ttl', default=7200)


class EditRecord(CLIRunnable):
    """ update resource records (bulk/single)"""
    action = 'edit'

    @staticmethod
    def add_record_arguments(parser):
        add_record_arguments(parser)
        parser.add_argument('--data', default=None)
        parser.add_argument('--ttl', default=None)
        parser.add_argument('--id', type=int, default=None)

    @staticmethod
    def execute(client, args):
        manager = DNSManager(client)
        results = manager.search_record(
            args.domain,
            args.record)

        for r in results:
            if args.id and r['id'] != args.id:
                continue
            r['data'] = args.data or r['data']
            r['ttl'] = args.ttl or r['ttl']
            manager.edit_record(r)


class RecordSearch(CLIRunnable):
    """ look for a resource record by exact name"""
    action = 'search'

    @staticmethod
    def add_additional_args(parser):
        add_record_arguments(parser)

    @staticmethod
    def execute(client, args):
        manager = DNSManager(client)
        results = manager.search_record(
            args.domain,
            args.record)

        t = Table([
            'id',
            'type',
            'ttl',
            'data',
        ])

        t.align['ttl'] = 'c'

        for r in results:
            t.add_row([
                r['id'],
                r['type'],
                r['ttl'],
                r['data'],
            ])

        return t


class RecordRemove(CLIRunnable):
    """ remove resource records"""
    action = 'remove'

    @staticmethod
    def add_additional_args(parser):
        add_record_arguments(parser)
        parser.add_argument('--id', type=int, default=None)

    @staticmethod
    def execute(client, args):
        manager = DNSManager(client)

        if args.id:
            records = [{'id': args.id}]
        else:
            records = manager.search_record(
                args.domain,
                args.record)

        if args.really or no_going_back('yes'):
            t = Table(['record'])
            for r in records:
                if not args.id or args.id == r['id']:
                    manager.delete_record(r['id'])
                    t.add_row(r['id'])

            return t
        else:
            print("Aborted.")
