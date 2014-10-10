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

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers

import re

RECORD_REGEX = re.compile(r"""^((?P<domain>([\w-]+(\.)?)*|\@)?\s+
                               (?P<ttl>\d+)?\s+
                               (?P<class>\w+)?)?\s+
                               (?P<type>\w+)\s+
                               (?P<data>.*)""", re.X)


class DumpZone(environment.CLIRunnable):
    """
usage: sl dns print <zone> [options]

print zone in BIND format

Arguments:
  <zone>    Zone name (softlayer.com)
"""
    action = "print"

    def execute(self, args):
        manager = SoftLayer.DNSManager(self.client)
        zone_id = helpers.resolve_id(manager.resolve_ids, args['<zone>'],
                                     name='zone')
        return manager.dump_zone(zone_id)


class CreateZone(environment.CLIRunnable):
    """
usage: sl dns create <zone> [options]

Create a zone

Arguments:
  <zone>    Zone name (softlayer.com)
"""
    action = 'create'

    def execute(self, args):
        manager = SoftLayer.DNSManager(self.client)
        manager.create_zone(args['<zone>'])


class DeleteZone(environment.CLIRunnable):
    """
usage: sl dns delete <zone> [options]

Delete zone

Arguments:
  <zone>    Zone name (softlayer.com)
"""
    action = 'delete'
    options = ['confirm']

    def execute(self, args):
        manager = SoftLayer.DNSManager(self.client)
        zone_id = helpers.resolve_id(manager.resolve_ids, args['<zone>'],
                                     name='zone')

        if args['--really'] or formatting.no_going_back(args['<zone>']):
            manager.delete_zone(zone_id)
        else:
            raise exceptions.CLIAbort("Aborted.")


class ImportZone(environment.CLIRunnable):
    """
usage: sl dns import <file> [options]

Creates a new zone based off a nicely BIND formatted file

Arguments:
    <file> Path to the bind zone file you want to import
Options:
    --dry-run  Don't actually do anything. This will show you what is parsed

    """
    action = 'import'

    def execute(self, args):

        dry_run = args.get('--dry-run')

        manager = SoftLayer.DNSManager(self.client)
        with open(args['<file>']) as zone_file:
            zone_contents = zone_file.read()

        zone, records, bad_lines = parse_zone_details(zone_contents)

        self.env.out("Parsed: zone=%s" % zone)
        for record in records:
            self.env.out("Parsed: %s" % record)
        for line in bad_lines:
            self.env.out("Unparsed: %s" % line)

        if dry_run:
            return

        # Find zone id or create the zone if it doesn't exist
        try:
            zone_id = helpers.resolve_id(manager.resolve_ids, zone,
                                         name='zone')
        except exceptions.CLIAbort:
            zone_id = manager.create_zone(zone)['id']
            self.env.out("\033[92mCREATED ZONE:   %s\033[0m" % zone)

        # Attempt to create each record
        for record in records:
            try:
                manager.create_record(zone_id,
                                      record['record'],
                                      record['record_type'],
                                      record['data'],
                                      record['ttl'])
                self.env.out("\033[92mCreated: Host: %s\033[0m" % record)
            except SoftLayer.SoftLayerAPIError as ex:
                self.env.out("\033[91mFAILED: %s" % record)
                self.env.out("%s \033[0m" % ex)

        return "Finished"


def parse_zone_details(zone_contents):
    """Parses a zone file into python data-structures"""
    records = []
    bad_lines = []
    zone_lines = [line.strip() for line in zone_contents.split('\n')]

    zone_search = re.search(r'^\$ORIGIN (?P<zone>.*)\.', zone_lines[0])
    zone = zone_search.group('zone')

    for line in zone_lines[1:]:
        record_search = re.search(RECORD_REGEX, line)
        if record_search is None:
            bad_lines.append(line)
            continue

        name = record_search.group('domain')
        # The API requires we send a host, although bind allows a blank
        # entry. @ is the same thing as blank
        if name is None:
            name = "@"

        ttl = record_search.group('ttl')
        # we don't do anything with the class
        # domain_class = domainSearch.group('class')
        record_type = record_search.group('type').upper()
        data = record_search.group('data')

        # the dns class doesn't support weighted MX records yet, so we chomp
        # that part out.
        if record_type == "MX":
            record_search = re.search(r'(?P<weight>\d+)\s+(?P<data>.*)', data)
            data = record_search.group('data')

        # This will skip the SOA record bit. And any domain that gets
        # parsed oddly.
        if record_type == 'IN':
            bad_lines.append(line)
            continue

        records.append({
            'record': name,
            'record_type': record_type,
            'data': data,
            'ttl': ttl,
        })

    return zone, records, bad_lines


class ListZones(environment.CLIRunnable):
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
        manager = SoftLayer.DNSManager(self.client)
        table = formatting.Table(['id', 'record', 'type', 'ttl', 'value'])

        table.align['ttl'] = 'l'
        table.align['record'] = 'r'
        table.align['value'] = 'l'

        zone_id = helpers.resolve_id(manager.resolve_ids, args['<zone>'],
                                     name='zone')

        records = manager.get_records(
            zone_id,
            record_type=args.get('--type'),
            host=args.get('--record'),
            ttl=args.get('--ttl'),
            data=args.get('--data'),
        )

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
        manager = SoftLayer.DNSManager(self.client)
        zones = manager.list_zones()
        table = formatting.Table(['id', 'zone', 'serial', 'updated'])
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


class AddRecord(environment.CLIRunnable):
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
        manager = SoftLayer.DNSManager(self.client)

        zone_id = helpers.resolve_id(manager.resolve_ids, args['<zone>'],
                                     name='zone')

        manager.create_record(
            zone_id,
            args['<record>'],
            args['<type>'],
            args['<data>'],
            ttl=args['--ttl'] or 7200)


class EditRecord(environment.CLIRunnable):
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
        manager = SoftLayer.DNSManager(self.client)
        zone_id = helpers.resolve_id(manager.resolve_ids, args['<zone>'],
                                     name='zone')

        results = manager.get_records(
            zone_id,
            host=args['<record>'])

        for result in results:
            if args['--id'] and str(result['id']) != args['--id']:
                continue
            result['data'] = args['--data'] or result['data']
            result['ttl'] = args['--ttl'] or result['ttl']
            manager.edit_record(result)


class RecordRemove(environment.CLIRunnable):
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
        manager = SoftLayer.DNSManager(self.client)
        zone_id = helpers.resolve_id(manager.resolve_ids, args['<zone>'],
                                     name='zone')

        if args['--id']:
            records = [{'id': args['--id']}]
        else:
            records = manager.get_records(
                zone_id,
                host=args['<record>'])

        if args['--really'] or formatting.no_going_back('yes'):
            table = formatting.Table(['record'])
            for result in records:
                manager.delete_record(result['id'])
                table.add_row([result['id']])

            return table
        raise exceptions.CLIAbort("Aborted.")
