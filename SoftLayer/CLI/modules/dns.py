"""
usage: sl dns [<command>] [<args>...] [options]

Manage DNS

The available commands are:
  search  Look for a resource record by exact name
  edit    Update resource records (bulk/single)
  create  Create zone
  list    List zones or a zone's records
  remove  Remove resource records
  add     Add resource record
  print   Print zone in BIND format
  delete  Delete zone
"""
# :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
# :license: BSD, see LICENSE for more details.

from SoftLayer.CLI import CLIRunnable, no_going_back, Table, CLIAbort
from SoftLayer import DNSManager, DNSZoneNotFound


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
        try:
            return manager.dump_zone(manager.get_zone(args['<zone>'])['id'])
        except DNSZoneNotFound:
            raise CLIAbort("No zone found matching: %s" % args['<zone>'])


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
            zone_id = manager.get_zone(args['<zone>'])
            manager.delete_zone(zone_id)
        raise CLIAbort("Aborted.")


class ListZones(CLIRunnable):
    """
usage: sl dns list [<zone>] [options]

List zones and optionally, records

Filters:
  --type=TYPE    Record type, such as A or CNAME
  --data=DATA    Record data, such as an IP address
  --record=HOST  Host record, such as www
  --ttl=TTL      TTL value in seconds, such as 86400
"""
    action = 'list'

    @classmethod
    def execute(cls, client, args):
        if args['<zone>']:
            return cls.list_zone(client, args['<zone>'], args)

        return cls.list_zones()

    @staticmethod
    def list_zone(client, zone, args):
        manager = DNSManager(client)
        t = Table([
            "record",
            "type",
            "ttl",
            "value",
        ])

        t.align['ttl'] = 'l'
        t.align['record'] = 'r'
        t.align['value'] = 'l'

        try:
            records = manager.get_records(args['<zone>'],
                    type=args.get('--type'),
                    host=args.get('--record'),
                    ttl=args.get('--ttl'),
                    data=args.get('--data'),
                )
        except DNSZoneNotFound:
            raise CLIAbort("No zone found matching: %s" % args['<zone>'])

        for rr in records:
            t.add_row([
                rr['host'],
                rr['type'].upper(),
                rr['ttl'],
                rr['data']
            ])

        return t

    @staticmethod
    def list_zones(client):
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
        try:
            zone = manager.get_zone(args['<zone>'])['id']
        except DNSZoneNotFound:
            raise CLIAbort("No zone found matching: %s" % args['<zone>'])
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
        try:
            results = manager.search_record(
                args['<zone>'],
                args['<record>'])
        except DNSZoneNotFound:
            raise CLIAbort("No zone found matching: %s" % args['<zone>'])

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
        results = []
        try:
            results = manager.search_record(
                args['<zone>'],
                args['<record>'])
        except DNSZoneNotFound:
            raise CLIAbort("No zone found matching: %s" % args['<zone>'])

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
            try:
                records = manager.search_record(
                    args['<zone>'],
                    args['<record>'])
            except DNSZoneNotFound:
                raise CLIAbort("No zone found matching: %s" % args['<zone>'])

        if args['--really'] or no_going_back('yes'):
            t = Table(['record'])
            for r in records:
                if args.get('--id') and args['--id'] != r['id']:
                    continue
                manager.delete_record(r['id'])
                t.add_row([r['id']])

            return t
        raise CLIAbort("Aborted.")
