"""
usage: sl dns [<command>] [<args>...] [options]

Manage DNS

The available commands are:
  search  Look for a resource record by exact name
  edit    Update resource records (bulk/single)
  create  Create zone
  list    List zones
  remove  Remove resource records
  add     Add resource record
  print   Print zone in BIND format
  delete  Delete zone

    :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
    :license: BSD, see LICENSE for more details.
"""
from SoftLayer.CLI import CLIRunnable, no_going_back, Table, CLIAbort
from SoftLayer.DNS import DNSManager


def add_zone_arguments(parser):
    parser.add_argument('domain')


def add_record_arguments(parser):
    add_zone_arguments(parser)
    parser.add_argument('record')


class DumpZone(CLIRunnable):
    """
usage: sl dns print <domain> [options]

print zone in BIND format
"""
    action = "print"

    @staticmethod
    def execute(client, args):
        manager = DNSManager(client)
        return manager.dump_zone(manager.get_zone(args['<domain>'])['id'])


class CreateZone(CLIRunnable):
    """
usage: sl dns create <domain> [options]

Create a zone
"""
    action = 'create'

    @staticmethod
    def execute(client, args):
        manager = DNSManager(client)
        manager.create_zone(args['<domain>'])
        return "Created zone: %s" % args['<domain>']


class DeleteZone(CLIRunnable):
    """
usage: sl dns delete <domain> <zone> [options]

Delete zone
"""
    action = 'delete'
    options = ['confirm']

    @staticmethod
    def execute(client, args):
        manager = DNSManager(client)
        if args['--really'] or no_going_back(args['<domain>']):
            manager.delete_zone(args['<domain>'])
            return "Deleted zone: %s" % args['<domain>']
        raise CLIAbort("Aborted.")


class ListZones(CLIRunnable):
    """
usage: sl dns list [options]

List zones
"""
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
    """
usage: sl dns add <domain> <record> <type> <data> [--ttl=TTL] [options]

Add resource record

Options:
  type       Record type. [Options: A, AAAA, CNAME, MX, NS, PTR, SPF, SRV, TXT]
  --ttl=TTL  Time to live [default: 7200]
"""
    action = 'add'

    @staticmethod
    def execute(client, args):
        manager = DNSManager(client)
        zone = manager.get_zone(args['<domain>'])['id']
        manager.create_record(
            zone,
            args['<record>'],
            args['<type>'],
            args['<data>'],
            ttl=args['--ttl'])


class EditRecord(CLIRunnable):
    """
usage: sl dns edit <domain> <record> [--data=DATA] [--ttl=TTL] [--id=ID]
                   [options]

Update resource records (bulk/single)

Options:
  --data=DATA
  --ttl=TTL    Time to live [default: 7200]
  --id=ID      Modify only the given ID
"""
    action = 'edit'

    @staticmethod
    def execute(client, args):
        manager = DNSManager(client)
        results = manager.search_record(
            args['<domain>'],
            args['<record>'])

        for r in results:
            if args['--id'] and r['id'] != args['--id']:
                continue
            r['data'] = args['--data'] or r['data']
            r['ttl'] = args['--ttl'] or r['ttl']
            manager.edit_record(r)


class RecordSearch(CLIRunnable):
    """
usage: sl dns search <domain> <record> [options]

Look for a resource record by exact name
"""
    action = 'search'

    @staticmethod
    def execute(client, args):
        manager = DNSManager(client)
        results = manager.search_record(
            args['<domain>'],
            args['<record>'])

        t = Table(['id', 'type', 'ttl', 'data'])

        t.align['ttl'] = 'c'

        for r in results:
            t.add_row([r['id'], r['type'], r['ttl'], r['data']])

        return t


class RecordRemove(CLIRunnable):
    """
usage: sl dns remove <domain> <record> [--id=ID] [options]

Remove resource records

Options:
  --id=ID  Remove only the given ID
"""
    action = 'remove'
    options = ['confirm']

    @staticmethod
    def execute(client, args):
        manager = DNSManager(client)

        if args['--id']:
            records = [{'id': args['--id']}]
        else:
            records = manager.search_record(
                args['<domain>'],
                args['<record>'])

        if args['--really'] or no_going_back('yes'):
            t = Table(['record'])
            for r in records:
                if args.get('--id') and args['--id'] != r['id']:
                    continue
                manager.delete_record(r['id'])
                t.add_row([r['id']])

            return t
        raise CLIAbort("Aborted.")
