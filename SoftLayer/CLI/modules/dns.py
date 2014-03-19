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
        """ list records for a particular zone """
        manager = DNSManager(self.client)
        table = Table([
            "id",
            "record",
            "type",
            "ttl",
            "value",
        ])

        table.align['ttl'] = 'l'
        table.align['record'] = 'r'
        table.align['value'] = 'l'

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

        for record in records:
            table.add_row([
                record['id'],
                record['host'],
                record['type'].upper(),
                record['ttl'],
                record['data']
            ])

        return table

    def list_all_zones(self):
        """ List all zones """
        manager = DNSManager(self.client)
        zones = manager.list_zones()
        table = Table([
            "id",
            "zone",
            "serial",
            "updated",
        ])
        table.align['serial'] = 'c'
        table.align['updated'] = 'c'

        for zone in zones:
            table.add_row([
                zone['id'],
                zone['name'],
                zone['serial'],
                zone['updateDate'],
            ])

        return table


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

        for result in results:
            if args['--id'] and str(result['id']) != args['--id']:
                continue
            result['data'] = args['--data'] or result['data']
            result['ttl'] = args['--ttl'] or result['ttl']
            manager.edit_record(result)


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
            table = Table(['record'])
            for result in records:
                if args.get('--id') and args['--id'] != result['id']:
                    continue
                manager.delete_record(result['id'])
                table.add_row([result['id']])

            return table
        raise CLIAbort("Aborted.")
