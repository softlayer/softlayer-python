"""
usage: sl dns [<command>] [<args>...] [options]

Manage DNS

The available zone commands are:
  create  Create zone
  delete  Delete zone
  list    List zones or a zone's records
  print   Print zone in BIND format
  import  Import a BIND style zone file

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
usage: sl dns import <file> [--dryRun]

Creates a new zone based off a nicely BIND formatted file

Arguments:
    <file> Path to the bind zone file you want to import
Options:
    --dryRun    don't actually do anything. This will show you what we were able to parse. 

    """
    action = 'import'
    def execute(self,args):
        import re
        dryRun = args.get('--dryRun')

        manager = SoftLayer.DNSManager(self.client)
        lines = [line.strip() for line in open(args['<file>'])]
        zoneSearch = re.search('^\$ORIGIN (?P<zone>.*)\.',lines[0])
        zone = zoneSearch.group('zone')

        if (dryRun):
            print  "Starting up a dry run for %s..." % (zone) 
            zone_id = 0
        else:
            try:
                zone_id = helpers.resolve_id(manager.resolve_ids, zone,name='zone')
            except :
                print "\033[92mCREATED ZONE:   %s\033[0m" % (zone)
                manager.create_zone(zone)
                zone_id = helpers.resolve_id(manager.resolve_ids, zone,name='zone')

        for content in lines[1:]:
            domainSearch = re.search('^((?P<domain>([\w-]+(\.)?)*|\@)?\s+(?P<ttl>\d+)?\s+(?P<class>\w+)?)?\s+(?P<type>\w+)\s+(?P<record>.*)',content)
            if (domainSearch is None): 
                print "\033[92mFailed: unknown line:   %s\033[0m" % (content)
            else:
                domainName = domainSearch.group('domain')
                #The API requires we send a host, although bind allows a blank entry. @ is the same thing as blank
                if (domainName is None):
                    domainName = "@"

                domainttl = domainSearch.group('ttl')
                domainClass = domainSearch.group('class')
                domainType = domainSearch.group('type')
                domainRecord = domainSearch.group('record')

                #This will skip the SOA record bit. And any domain that gets parsed oddly.
                if (domainType.upper() == 'IN'):
                    print "SKIPPED: Host: %s TTL: %s Type: %s Record: %s" % (domainName,domainttl,domainType,domainRecord) 
                    continue

                #the dns class doesn't support weighted MX records yet, so we chomp that part out. 
                if (domainType.upper() == "MX"):
                    recordSearch = re.search('(?P<weight>\d+)\s+(?P<record>.*)',domainRecord)
                    domainRecord = recordSearch.group('record')

                try:
                    if (dryRun):
                        print "Parsed: Host: %s TTL: %s Type: %s Record: %s" % (domainName,domainttl,domainType,domainRecord) 
                    else:
                        manager.create_record(zone_id,domainName,domainType,domainRecord,domainttl)
                        print "\033[92mCreated: Host: %s TTL: %s Type: %s Record: %s\033[0m" % (domainName,domainttl,domainType,domainRecord)
                except Exception, e:
                    print "\033[91mFAILED: Host: %s Type: %s Record: %s" % (domainName,domainType,domainRecord.upper())  
                    print "\t", e ,"\033[0m"


        return "Finished"


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
