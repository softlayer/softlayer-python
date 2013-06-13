"""
usage: sl hardware [<command>] [<args>...] [options]
       sl hardware [-h | --help]

Manage hardware

The available commands are:
  list      List hardware devices
  detail    Retrieve hardware details
  reload    Perform an OS reload

For several commands, <identifier> will be asked for. This can be the id,
hostname or the ip address for a piece of hardware.
"""
from SoftLayer.CLI.helpers import (
    CLIRunnable, Table, FormattedItem, NestedDict, CLIAbort, blank, listing,
    gb, no_going_back)
from SoftLayer import HardwareManager


def resolve_id(manager, identifier):
    ids = manager.resolve_ids(identifier)

    if len(ids) == 0:
        raise CLIAbort("Error: Unable to find hardware '%s'" % identifier)

    if len(ids) > 1:
        raise CLIAbort(
            "Error: Multiple hardware found for '%s': %s" %
            (identifier, ', '.join([str(_id) for _id in ids])))

    return ids[0]


class ListHardware(CLIRunnable):
    """
usage: sl hardware list [options]

List hardware servers on the acount

Examples:
    sl hardware list --datacenter=dal05
    sl hardware list --network=100 --domain=example.com
    sl hardware list --tags=production,db

Options:
  --sortby=ARG  Column to sort by. options: id, datacenter, host, cores,
                  memory, primary_ip, backend_ip

Filters:
  -H --hostname=HOST       Host portion of the FQDN. example: server
  -D --domain=DOMAIN       Domain portion of the FQDN. example: example.com
  -c --cpu=CPU             Number of CPU cores
  -m --memory=MEMORY       Memory in gigabytes
  -d DC, --datacenter=DC   datacenter shortname (sng01, dal05, ...)
  -n MBPS, --network=MBPS  Network port speed in Mbps
  --tags=ARG               Only show instances that have one of these tags.
                           Comma-separated. (production,db)

For more on filters see 'sl help filters'
"""
    action = 'list'

    @staticmethod
    def execute(client, args):
        manager = HardwareManager(client)

        tags = None
        if args.get('--tags'):
            tags = [tag.strip() for tag in args.get('--tags').split(',')]

        servers = manager.list_hardware(
            hostname=args.get('--hostname'),
            domain=args.get('--domain'),
            cpus=args.get('--cpu'),
            memory=args.get('--memory'),
            datacenter=args.get('--datacenter'),
            nic_speed=args.get('--network'),
            tags=tags)

        t = Table([
            'id',
            'datacenter',
            'host',
            'cores',
            'memory',
            'primary_ip',
            'backend_ip'
        ])
        t.sortby = args.get('--sortby') or 'host'

        for server in servers:
            server = NestedDict(server)
            t.add_row([
                server['id'],
                server['datacenter']['name'] or blank(),
                server['fullyQualifiedDomainName'],
                server['processorCoreAmount'],
                gb(server['memoryCapacity']),
                server['primaryIpAddress'] or blank(),
                server['primaryBackendIpAddress'] or blank(),
            ])

        return t


class HardwareDetails(CLIRunnable):
    """
usage: sl hardware detail [--passwords] [--price] <identifier> [options]

Get details for a hardware device

Options:
  --passwords  Show passwords (check over your shoulder!)
  --price      Show associated prices
"""
    action = 'detail'

    @staticmethod
    def execute(client, args):
        hardware = HardwareManager(client)

        t = Table(['Name', 'Value'])
        t.align['Name'] = 'r'
        t.align['Value'] = 'l'

        hardware_id = resolve_id(hardware, args.get('<identifier>'))
        result = hardware.get_hardware(hardware_id)
        result = NestedDict(result)

        t.add_row(['id', result['id']])
        t.add_row(['hostname', result['fullyQualifiedDomainName']])
        t.add_row(['status', result['hardwareStatus']['status']])
        t.add_row(['datacenter', result['datacenter']['name'] or blank()])
        t.add_row(['cores', result['processorCoreAmount']])
        t.add_row(['memory', gb(result['memoryCapacity'])])
        t.add_row(['public_ip', result['primaryIpAddress'] or blank()])
        t.add_row(
            ['private_ip', result['primaryBackendIpAddress'] or blank()])
        t.add_row([
            'os',
            FormattedItem(
                result['operatingSystem']['softwareLicense']
                ['softwareDescription']['referenceCode'] or blank(),
                result['operatingSystem']['softwareLicense']
                ['softwareDescription']['name'] or blank()
            )])
        t.add_row(['created', result['provisionDate']])
        if result.get('notes'):
            t.add_row(['notes', result['notes']])

        if args.get('--price'):
            t.add_row(['price rate', result['billingItem']['recurringFee']])

        if args.get('--passwords'):
            user_strs = []
            for item in result['operatingSystem']['passwords']:
                user_strs.append(
                    "%s %s" % (item['username'], item['password']))
            t.add_row(['users', listing(user_strs)])

        tag_row = []
        for tag in result['tagReferences']:
            tag_row.append(tag['tag']['name'])

        if tag_row:
            t.add_row(['tags', listing(tag_row, separator=',')])

        ptr_domains = client['Hardware_Server'].getReverseDomainRecords(
            id=hardware_id)

        for ptr_domain in ptr_domains:
            for ptr in ptr_domain['resourceRecords']:
                t.add_row(['ptr', ptr['data']])

        return t


class HardwareReload(CLIRunnable):
    """
usage: sl hardware reload <identifier> [options]

Reload the OS on a hardware server based on its current configuration
"""

    action = 'reload'
    options = ['confirm']

    @staticmethod
    def execute(client, args):
        hardware = HardwareManager(client)
        hardware_id = resolve_id(hardware, args.get('<identifier>'))
        if args['--really'] or no_going_back(hardware_id):
            hardware.reload(hardware_id)
        else:
            CLIAbort('Aborted')
