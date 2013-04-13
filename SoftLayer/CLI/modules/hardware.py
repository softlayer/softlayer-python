"""
usage: sl hardware [<command>] [<args>...] [options]
       sl hardware [-h | --help]

Manage hardware

The available commands are:
  list      List hardware devices
  detail    Retrieve hardware details
"""
from SoftLayer.CLI.helpers import CLIRunnable, Table, FormattedItem, NestedDict, blank, listing
from SoftLayer.hardware import HardwareManager


class ListHardware(CLIRunnable):
    """
usage: sl hardware list [options]

List hardware servers on the acount
"""
    action = 'list'

    @staticmethod
    def execute(client, args):
        manager = HardwareManager(client)

        servers = manager.list_hardware()
        t = Table(['id', 'hostname', 'domain'])
        for server in servers:
            t.add_row([
                server['id'],
                server['hostname'],
                server['domain']
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

        hardware_id = hardware, args.get('<identifier>')
        result = hardware.get_hardware(hardware_id[1])
        result = NestedDict(result)

        t.add_row(['id', result['id']])
        t.add_row(['hostname', result['fullyQualifiedDomainName']])
        t.add_row(['datacenter', result['datacenter'].get('name', blank())])
        t.add_row(['provisionDate', result['provisionDate']])
        t.add_row(['public_ip', result.get('primaryIpAddress', blank())])
        t.add_row(
            ['private_ip', result.get('primaryBackendIpAddress', blank())])
        t.add_row([
            'os',
            FormattedItem(
                result['operatingSystem']['softwareLicense']
                ['softwareDescription'].get('referenceCode', blank()),
                result['operatingSystem']['softwareLicense']
                ['softwareDescription'].get('name', blank())
            )])
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

        ptr_domains = client['Hardware_Server'].\
            getReverseDomainRecords(id=hardware_id[1])

        for ptr_domain in ptr_domains:
            for ptr in ptr_domain['resourceRecords']:
                t.add_row(['ptr', ptr['data']])

        return t
