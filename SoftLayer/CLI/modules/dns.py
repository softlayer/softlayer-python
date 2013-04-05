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
"""
# :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
# :license: BSD, see LICENSE for more details.

from SoftLayer.CLI import CLIRunnable, no_going_back, Table, CLIAbort
from SoftLayer.DNS import DNSManager


class DumpZone(CLIRunnable):
    """
usage: sl dns print <zone> [options]

print zone in BIND format

Arguments:
  <zone>    Zone name (softlayer.com)
"""
    action = "print"

    @staticmethod
    def execute(client, args):
        manager = DNSManager(client)
        return manager.dump_zone(manager.get_zone(args['<zone>'])['id'])


class CreateZone(CLIRunnable):
    """
usage: sl dns create <zone> [options]

Create a zone

Arguments:
  <zone>    Zone name (softlayer.com)
"""
    action = 'create'

    @staticmethod
    def execute(client, args):
        manager = DNSManager(client)
        manager.create_zone(args['<zone>'])
        return "Created zone: %s" % args['<zone>']


class DeleteZone(CLIRunnable):
    """
usage: sl dns delete <zone> [options]

Delete zone

Arguments:
  <zone>    Zone name (softlayer.com)
"""
    action = 'delete'
    options = ['confirm']

    @staticmethod
    def execute(client, args):
        manager = DNSManager(client)
        if args['--really'] or no_going_back(args['<zone>']):
            manager.delete_zone(args['<zone>'])
            return "Deleted zone: %s" % args['<zone>']
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
usage: sl dns add <zone> <record> <type> <data> [--ttl=TTL] [options]

Add resource record

Arguments:
  <zone>    Zone name (softlayer.com)
  <record>  Resource record (www)
  <type>    Record type. [Options: A, AAAA,
              CNAME, MX, NS, PTR, SPF, SRV, TXT]
  <data>    Record data. NOTE: only minor validation is done

Options:
  --ttl=TTL  Time to live [default: 7200]
"""
    action = 'add'

    @staticmethod
    def execute(client, args):
        manager = DNSManager(client)
        zone = manager.get_zone(args['<zone>'])['id']
        manager.create_record(
            zone,
            args['<record>'],
            args['<type>'],
            args['<data>'],
            ttl=args['--ttl'])


class EditRecord(CLIRunnable):
    """
usage: sl dns edit <zone> <record> [--data=DATA] [--ttl=TTL] [--id=ID]
                   [options]

Update resource records (bulk/single)

Arguments:
  <zone>    Zone name (softlayer.com)
  <record>  Resource record (www)

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
            args['<zone>'],
            args['<record>'])

        for r in results:
            if args['--id'] and r['id'] != args['--id']:
                continue
            r['data'] = args['--data'] or r['data']
            r['ttl'] = args['--ttl'] or r['ttl']
            manager.edit_record(r)


class RecordSearch(CLIRunnable):
    """
usage: sl dns search <zone> <record> [options]

Look for a resource record by exact name

Arguments:
  <zone>    Zone name (softlayer.com)
  <record>  Resource record (www)
"""
    action = 'search'

    @staticmethod
    def execute(client, args):
        manager = DNSManager(client)
        results = manager.search_record(
            args['<zone>'],
            args['<record>'])

        t = Table(['id', 'type', 'ttl', 'data'])

        t.align['ttl'] = 'c'

        for r in results:
            t.add_row([r['id'], r['type'], r['ttl'], r['data']])

        return t


class RecordRemove(CLIRunnable):
    """
usage: sl dns remove <zone> <record> [--id=ID] [options]

Remove resource records

Arguments:
  <zone>    Zone name (softlayer.com)
  <record>  Resource record (www)

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
                args['<zone>'],
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
