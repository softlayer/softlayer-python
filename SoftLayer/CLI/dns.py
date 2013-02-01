#!/usr/bin/env python
"""Manages DNS"""

from SoftLayer.CLI import CLIRunnable, no_going_back
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
        print(manager.dump_zone(manager.get_zone(args.domain)['id']))


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
        print "Created zone:", args.domain


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
            print "Deleted zone:", args.domain
        else:
            print "Aborted."


class ListZones(CLIRunnable):
    """ list zones """
    action = 'list'

    @staticmethod
    def execute(client, args):
        manager = DNSManager(client)
        zones = manager.list_zones()
        print "{0:.^10}|{1:.^30}|{2:.^10}|{3:.^30}".format(
            'id', 'zone', 'serial', 'last updated')
        fmt = (
            "{0[id]:<10d} {0[name]:<30s} {0[serial]:^10d} "
            "{0[updateDate]:^30}")
        for z in zones:
            print fmt.format(z)


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

        print "Results for {0}.{1}".format(
            args.record,
            args.domain)
        print "{0:.^10}|{1:.<4}|{2:.^7}|{3:.^70}".format(
            'id', 'type', 'ttl', 'data')
        fmt = "{0[id]:<10} {0[type]:<4} {0[ttl]:^7} {0[data]:<}"
        for r in results:
            print fmt.format(r)


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
        records = manager.search_record(
            args.domain,
            args.record)

        if not args.id:
            print "Deleting %d records" % len(records)

        if args.really or no_going_back('yes'):
            for r in records:
                if not args.id or args.id == r['id']:
                    manager.delete_record(r['id'])
                    print "Deleted %s" % r
        else:
            print "Aborted."
