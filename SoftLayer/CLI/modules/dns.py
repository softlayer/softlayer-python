"""
usage: sl dns [<command>] [<args>...] [options]

Manage DNS

The available zone commands are:
  create  Create zone
  delete  Delete zone
  list    List zones or a zone's records
  print   Print zone in BIND format

The available record commands are:
  add     Add resource record
  edit    Update resource records (bulk/single)
  remove  Remove resource records
"""
# :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
# :license: MIT, see LICENSE for more details.

from SoftLayer.CLI import (
    CLIRunnable, no_going_back, Table, CLIAbort, resolve_id)
from SoftLayer import DNSManager, DNSZoneNotFound


class DumpZone(CLIRunnable):
    """
usage: sl dns print <zone> [options]

print zone in BIND format

Arguments:
  <zone>    Zone name (softlayer.com)
"""
    action = "print"

    def execute(self, args):
        manager = DNSManager(self.client)
        zone_id = resolve_id(manager.resolve_ids, args['<zone>'], name='zone')
        try:
            return manager.dump_zone(zone_id)
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

    def execute(self, args):
        manager = DNSManager(self.client)
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

    def execute(self, args):
        manager = DNSManager(self.client)
        zone_id = resolve_id(manager.resolve_ids, args['<zone>'], name='zone')

        if args['--really'] or no_going_back(args['<zone>']):
            manager.delete_zone(zone_id)
        else:
            raise CLIAbort("Aborted.")


class ListZones(CLIRunnable):
    """
usage: sl dns list [<zone>] [options]

List zones and optionally, records

Filters:
  --data=DATA    Record data, such as an IP address
  --record=HOST  Host record, such as www
  --ttl=TTL      TTL value in seconds, such as 86400
  --type=TYPE    Record type, such as A or CNAME
"""
    action = 'list'

    def execute(self, args):
        if args['<zone>']:
            return self.list_zone(args)

        return self.list_all_zones()

    def list_zone(self, args):
        manager = DNSManager(self.client)
        t = Table([
            "record",
            "type",
            "ttl",
            "value",
        ])

        t.align['ttl'] = 'l'
        t.align['record'] = 'r'
        t.align['value'] = 'l'

        zone_id = resolve_id(manager.resolve_ids, args['<zone>'], name='zone')

        try:
            records = manager.get_records(
                zone_id,
                record_type=args.get('--type'),
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

    def list_all_zones(self):
        manager = DNSManager(self.client)
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
  --ttl=TTL  Time to live
"""
    action = 'add'

    def execute(self, args):
        manager = DNSManager(self.client)

        zone_id = resolve_id(manager.resolve_ids, args['<zone>'], name='zone')
        args['--ttl'] = args['--ttl'] or 7200

        manager.create_record(
            zone_id,
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
  --id=ID      Modify only the given ID
  --ttl=TTL    Time to live
"""
    action = 'edit'

    def execute(self, args):
        manager = DNSManager(self.client)
        zone_id = resolve_id(manager.resolve_ids, args['<zone>'], name='zone')

        try:
            results = manager.get_records(
                zone_id,
                host=args['<record>'])
        except DNSZoneNotFound:
            raise CLIAbort("No zone found matching: %s" % args['<zone>'])

        for r in results:
            if args['--id'] and r['id'] != args['--id']:
                continue
            r['data'] = args['--data'] or r['data']
            r['ttl'] = args['--ttl'] or r['ttl']
            manager.edit_record(r)


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

    def execute(self, args):
        manager = DNSManager(self.client)
        zone_id = resolve_id(manager.resolve_ids, args['<zone>'], name='zone')

        if args['--id']:
            records = [{'id': args['--id']}]
        else:
            try:
                records = manager.get_records(
                    zone_id,
                    host=args['<record>'])
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
