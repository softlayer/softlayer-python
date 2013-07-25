"""
usage: sl hardware [<command>] [<args>...] [options]
       sl hardware [-h | --help]

Manage hardware

The available commands are:
  list      List hardware devices
  detail    Retrieve hardware details
  reload    Perform an OS reload
  cancel    Cancel a dedicated server.
  cancel-reasons  Provides the list of possible cancellation reasons
  network   Manage network settings
  list-chassis    Provide a list of all chassis available for ordering
  create-options  Display a list of creation options for a specific chassis
  create    Create a new dedicated server

For several commands, <identifier> will be asked for. This can be the id,
hostname or the ip address for a piece of hardware.
"""
import re
import os
from os import linesep
from SoftLayer.CLI.helpers import (
    CLIRunnable, Table, FormattedItem, NestedDict, CLIAbort, blank, listing,
    SequentialOutput, gb, no_going_back, resolve_id, confirm, ArgumentError)
from SoftLayer import HardwareManager


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

        hardware_id = resolve_id(
            hardware.resolve_ids, args.get('<identifier>'), 'hardware')
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

Optional:
    -i, --postinstall=URI   Post-install script to download
                             (Only HTTPS executes, HTTP leaves file in /root)
"""

    action = 'reload'
    options = ['confirm']

    @staticmethod
    def execute(client, args):
        hardware = HardwareManager(client)
        hardware_id = resolve_id(
            hardware.resolve_ids, args.get('<identifier>'), 'hardware')
        if args['--really'] or no_going_back(hardware_id):
            hardware.reload(hardware_id, args['--postinstall'])
        else:
            CLIAbort('Aborted')


class CancelHardware(CLIRunnable):
    """
usage: sl hardware cancel <identifier> [options]

Cancel a dedicated server

Options:
  --reason   An optional cancellation reason. See cancel-reasons for a list of
             available options.
"""

    action = 'cancel'
    options = ['confirm']

    @staticmethod
    def execute(client, args):
        hw = HardwareManager(client)
        hw_id = resolve_id(hw, args.get('<identifier>'))

        print "(Optional) Add a cancellation comment:",
        comment = raw_input()

        reason = args.get('--reason')

        if args['--really'] or no_going_back(hw_id):
            hw.cancel_hardware(hw_id, reason, comment)
        else:
            CLIAbort('Aborted')


class HardwareCancelReasons(CLIRunnable):
    """
usage: sl hardware cancel-reasons

Display a list of cancellation reasons
"""

    action = 'cancel-reasons'

    @staticmethod
    def execute(client, args):
        t = Table(['Code', 'Reason'])
        t.align['Code'] = 'r'
        t.align['Reason'] = 'l'

        mgr = HardwareManager(client)
        reasons = mgr.get_cancellation_reasons().iteritems()

        for code, reason in reasons:
            t.add_row([code, reason])

        return t


class NetworkHardware(CLIRunnable):
    """
usage: sl hardware network port <identifier> --speed=SPEED
                                (--public | --private) [options]

Manage network settings

Options:
    --speed=SPEED  Port speed. 0 disables the port.
                   [Options: 0, 10, 100, 1000, 10000]
    --public       Public network
    --private      Private network
"""
    action = 'network'

    @classmethod
    def execute(cls, client, args):
        if args['port']:
            return cls.exec_port(client, args)

        if args['details']:
            return cls.exec_detail(client, args)

    @staticmethod
    def exec_port(client, args):
        public = True
        if args['--private']:
            public = False

        mgr = HardwareManager(client)
        hw_id = resolve_id(mgr.resolve_ids, args.get('<identifier>'),
                           'hardware')

        result = mgr.change_port_speed(hw_id, public, args['--speed'])
        if result:
            return "Success"
        else:
            return result

    @staticmethod
    def exec_detail(client, args):
        # TODO this should print out default gateway and stuff
        raise CLIAbort('Not implemented')


class ListChassisHardware(CLIRunnable):
    """
usage: sl hardware list-chassis

Display a list of chassis available for ordering dedicated servers.
"""
    action = 'list-chassis'

    @staticmethod
    def execute(client, args):
        t = Table(['Code', 'Chassis'])
        t.align['Code'] = 'r'
        t.align['Chassis'] = 'l'

        mgr = HardwareManager(client)
        chassis = mgr.get_available_dedicated_server_packages()

        for chassis in chassis:
            t.add_row([chassis[0], chassis[1]])

        return t


class HardwareCreateOptions(CLIRunnable):
    """
usage: sl hardware create-options <chassis_id> [options]

Output available available options when creating a dedicated server with the
specified chassis.

Options:
  --all         Show all options. default if no other option provided
  --datacenter  Show datacenter options
  --cpu         Show CPU options
  --nic         Show NIC speed options
  --disk        Show disk options
  --os          Show operating system options
  --memory      Show memory size options
  --controller  Show disk controller options
"""

    action = 'create-options'
    options = ['datacenter', 'cpu', 'memory', 'os', 'disk', 'nic',
               'controller']

    @classmethod
    def execute(cls, client, args):
        mgr = HardwareManager(client)

        t = Table(['Name', 'Value'])
        t.align['Name'] = 'r'
        t.align['Value'] = 'l'

        chassis_id = args.get('<chassis_id>')

        ds_options = mgr.get_dedicated_server_create_options(chassis_id)

        show_all = True
        for opt_name in cls.options:
            if args.get("--" + opt_name):
                show_all = False
                break

        if args['--all']:
            show_all = True

        if args['--datacenter'] or show_all:
            results = cls.get_create_options(ds_options, 'datacenter')[0]

            t.add_row([results[0], listing(sorted(results[1]))])

        if args['--cpu'] or show_all:
            results = cls.get_create_options(ds_options, 'cpu')

            for result in sorted(results):
                t.add_row([result[0], listing(
                    item[0] for item in sorted(result[1]))])

        if args['--memory'] or show_all:
            results = cls.get_create_options(ds_options, 'memory')[0]

            t.add_row([results[0], listing(
                item[0] for item in sorted(results[1]))])

        if args['--os'] or show_all:
            results = cls.get_create_options(ds_options, 'os')

            for result in results:
                t.add_row([result[0], linesep.join(
                    item[0] for item in sorted(result[1]))])

        if args['--disk'] or show_all:
            results = cls.get_create_options(ds_options, 'disk')[0]

            t.add_row([results[0], linesep.join(
                item[0] for item in sorted(results[1],))])

        if args['--nic'] or show_all:
            results = cls.get_create_options(ds_options, 'nic')

            for result in results:
                t.add_row([result[0], listing(
                    item[0] for item in sorted(result[1],))])

        if args['--controller'] or show_all:
            results = cls.get_create_options(ds_options, 'disk_controller')[0]

            t.add_row([results[0], listing(
                item[0] for item in sorted(results[1],))])

        return t

    @classmethod
    def get_create_options(cls, ds_options, section, pretty=True):
        """ This method can be used to parse the bare metal instance creation
        options into different sections. This can be useful for data validation
        as well as printing the options on a help screen.

        :param dict ds_options: The instance options to parse. Must come from
                                 the .get_bare_metal_create_options() function
                                 in the HardwareManager.
        :param string section: The section to parse out.
        :param bool pretty: If true, it will return the results in a 'pretty'
                            format that's easier to print.
        """
        if 'datacenter' == section:
            datacenters = [loc['keyname']
                           for loc in ds_options['locations']]
            return [('datacenter', datacenters)]
        elif 'cpu' == section:
            results = []
            cpu_regex = re.compile('\s(\w+)\s(\d+)\s+\-\s+([\d\.]+GHz)'
                                   '\s+\([\w ]+\)\s+\-\s+(.+)$')

            for item in ds_options['categories']['server']['items']:
                cpu = cpu_regex.search(item['description'])
                text = 'cpu: ' + cpu.group(1) + ' ' + cpu.group(2) + ' (' \
                       + cpu.group(3) + ', ' + cpu.group(4) + ')'

                if cpu:
                    results.append((text, [(cpu.group(2), item['price_id'])]))

            return results
        elif 'memory' == section:
            ram = []
            for option in ds_options['categories']['ram']['items']:
                ram.append((int(option['capacity']), option['price_id']))

            return [('memory', ram)]
        elif 'os' == section:
            os_regex = re.compile('(^[A-Za-z\s\/\-]+) ([\d\.]+)')
            bit_regex = re.compile(' \((\d+)\s*bit')
            extra_regex = re.compile(' - (.+)\(')

            # Encapsulate the code for generating the operating system code
            def _generate_os_code(name, version, bits, extra_info):
                name = name.replace(' Linux', '')
                name = name.replace('Enterprise', '')
                name = name.replace('GNU/Linux', '')

                os_code = name.strip().replace(' ', '_').upper()

                if os_code.startswith('RED_HAT'):
                    os_code = 'REDHAT'

                if 'UBUNTU' in os_code:
                    version = re.sub('\.\d+', '', version)

                os_code += '_' + version.replace('.0', '')

                if bits:
                    os_code += '_' + bits

                if extra_info:
                    garbage = ['Install', '(32 bit)', '(64 bit)']

                    for g in garbage:
                        extra_info = extra_info.replace(g, '')

                    os_code += '_' + \
                               extra_info.strip().replace(' ', '_').upper()

                return os_code

            # Also separate out the code for generating the Windows OS code
            # since it's significantly different from the rest.
            def _generate_windows_code(description):
                version_check = re.search('Windows Server (\d+)', description)
                version = version_check.group(1)

                os_code = 'WIN_' + version

                if 'Datacenter' in description:
                    os_code += '-DC'
                elif 'Enterprise' in description:
                    os_code += '-ENT'
                else:
                    os_code += '-STD'

                if 'ith R2' in description:
                    os_code += '-R2'
                elif 'ith Hyper-V' in description:
                    os_code += '-HYPERV'

                bit_check = re.search('\((\d+)\s*bit', description)
                if bit_check:
                    os_code += '_' + bit_check.group(1)

                return os_code

            # Loop through the operating systems and get their OS codes
            os_list = {}
            flat_list = []

            for os in ds_options['categories']['os']['items']:
                if 'Windows Server' in os['description']:
                    os_code = _generate_windows_code(os['description'])
                else:
                    os_results = os_regex.search(os['description'])
                    name = os_results.group(1)
                    version = os_results.group(2)
                    bits = bit_regex.search(os['description'])
                    extra_info = extra_regex.search(os['description'])

                    if bits:
                        bits = bits.group(1)
                    if extra_info:
                        extra_info = extra_info.group(1)

                    os_code = _generate_os_code(name, version, bits,
                                                extra_info)

                name = os_code.split('_')[0]

                if name not in os_list:
                    os_list[name] = []

                os_list[name].append((os_code, os['price_id']))
                flat_list.append((os_code, os['price_id']))

            if pretty:
                results = []
                for os in sorted(os_list.keys()):
                    results.append(('os (%s)' % os, os_list[os]))

                return results
            else:
                return [('os', flat_list)]

        elif 'disk' == section:
            disks = []
            type_regex = re.compile('^[\d\.]+[GT]B\s+(.+)$')
            for disk in ds_options['categories']['disk0']['items']:
                disk_type = 'SATA'
                disk_type = type_regex.match(disk['description']).group(1)

                disk_type = disk_type.replace('RPM', '').strip()
                disk_type = disk_type.replace(' ', '_').upper()
                disk_type = str(int(disk['capacity'])) + '_' + disk_type
                disks.append((disk_type, disk['price_id']))

            return [('disk', disks)]
        elif 'nic' == section:
            single = []
            dual = []

            for item in ds_options['categories']['port_speed']['items']:
                if 'dual' in item['description'].lower():
                    dual.append((str(int(item['capacity'])) + '_DUAL',
                                 item['price_id']))
                else:
                    single.append((int(item['capacity']), item['price_id']))

            return [('single nic', single), ('dual nic', dual)]
        elif 'disk_controller' == section:
            options = []
            for item in ds_options['categories']['disk_controller']['items']:
                text = item['description'].replace(' ', '')

                if 'Non-RAID' == text:
                    text = 'None'

                options.append((text, item['price_id']))

            return [('disk_controllers', options)]

        return []


class CreateHardware(CLIRunnable):
    """
usage: sl hardware create --hostname=HOST --domain=DOMAIN --cpu=CPU
    --chassis=CHASSIS --memory=MEMORY --os=OS --disk=SIZE... [options]

Order/create a dedicated server. See 'sl hardware list-chassis' and
'sl hardware create-options' for valid options

Required:
  -H --hostname=HOST  Host portion of the FQDN. example: server
  -D --domain=DOMAIN  Domain portion of the FQDN example: example.com
  --chassis=CHASSIS   The chassis to use for the new server
  -c --cpu=CPU        CPU model
  -o OS, --os=OS      OS install code.
  -m --memory=MEMORY  Memory in mebibytes (n * 1024)


Optional:
  -d DC, --datacenter=DC   datacenter name
                           Note: Omitting this value defaults to the first
                             available datacenter
  -n MBPS, --network=MBPS  Network port speed in Mbps
  --controller=RAID        The RAID configuration for the server.
                             Defaults to None.
  --dry-run, --test        Do not create the server, just get a quote
"""
    action = 'create'

    @classmethod
    def execute(cls, client, args):
        mgr = HardwareManager(client)

        ds_options = mgr.get_dedicated_server_create_options(args['--chassis'])

        order = {
            'hostname': args['--hostname'],
            'domain': args['--domain'],
            'bare_metal': False,
            'package_id': args['--chassis'],
        }

        # Convert the OS code back into a price ID
        os_price = cls._get_price_id_from_options(ds_options, 'os',
                                                  args['--os'])

        if os_price:
            order['os'] = os_price
        else:
            raise CLIAbort('Invalid operating system specified.')

        order['location'] = args['--datacenter'] or 'FIRST_AVAILABLE'
        order['server'] = cls._get_price_id_from_options(ds_options, 'cpu',
                                                         args['--cpu'])
        order['ram'] = cls._get_price_id_from_options(ds_options, 'memory',
                                                      int(args['--memory']))
        # Set the disk sizes
        disk_prices = []
        for disk in args.get('--disk'):
            disk_price = cls._get_price_id_from_options(ds_options, 'disk',
                                                        disk)

            if disk_price:
                disk_prices.append(disk_price)

        if not disk_prices:
            disk_prices.append(cls._get_default_value(ds_options, 'disk0'))

        order['disks'] = disk_prices

        # Set the disk controller price
        if args.get('--controller'):
            dc_price = cls._get_price_id_from_options(ds_options,
                                                      'disk_controller',
                                                      args.get('--controller'))
        else:
            dc_price = cls._get_price_id_from_options(ds_options,
                                                      'disk_controller',
                                                      'None')

        order['disk_controller'] = dc_price

        # Set the port speed
        port_speed = args.get('--network') or 10

        nic_price = cls._get_price_id_from_options(ds_options, 'nic',
                                                   port_speed)

        if nic_price:
            order['port_speed'] = nic_price
        else:
            raise CLIAbort('Invalid NIC speed specified.')

        # Begin output
        t = Table(['Item', 'cost'])
        t.align['Item'] = 'r'
        t.align['cost'] = 'r'

        if args.get('--test'):
            result = mgr.verify_order(**order)

            total = 0.0
            for price in result['prices']:
                total += float(price.get('recurringFee', 0.0))
                if args.get('--hourly'):
                    rate = "%.2f" % float(price['hourlyRecurringFee'])
                else:
                    rate = "%.2f" % float(price['recurringFee'])

                t.add_row([price['item']['description'], rate])

            billing_rate = 'monthly'
            if args.get('--hourly'):
                billing_rate = 'hourly'
            t.add_row(['Total %s cost' % billing_rate, "%.2f" % total])
            output = SequentialOutput(blanks=False)
            output.append(t)
            output.append(FormattedItem(
                '',
                ' -- ! Prices reflected here are retail and do not '
                'take account level discounts and are not guarenteed.')
            )
        elif args.get('--really') or confirm(
                "This action will incur charges on your account. Continue?"):
            result = mgr.place_order(**order)

            t = Table(['name', 'value'])
            t.align['name'] = 'r'
            t.align['value'] = 'l'
            t.add_row(['id', result['orderId']])
            t.add_row(['created', result['orderDate']])
            output = t
        else:
            raise CLIAbort('Aborting dedicated server order.')

        return output

    @classmethod
    def _get_default_value(cls, ds_options, option):
        if option not in ds_options['categories']:
            return

        for item in ds_options['categories'][option]['items']:
            if not any([
                    float(item['prices'][0].get('setupFee', 0)),
                    float(item['prices'][0].get('recurringFee', 0)),
                    float(item['prices'][0].get('hourlyRecurringFee', 0)),
                    float(item['prices'][0].get('oneTimeFee', 0)),
                    float(item['prices'][0].get('laborFee', 0)),
            ]):
                return item['price_id']

    @classmethod
    def _get_price_id_from_options(cls, ds_options, option, value):
        ds_obj = HardwareCreateOptions()
        price_id = None

        for k, v in ds_obj.get_create_options(ds_options, option, False):
            for item_options in v:
                if item_options[0] == value:
                    price_id = item_options[1]

        return price_id


class EditHardware(CLIRunnable):
    """
usage: sl hardware edit <identifier> [options]

Edit hardware details

Options:
  -H --hostname=HOST  Host portion of the FQDN. example: server
  -D --domain=DOMAIN  Domain portion of the FQDN example: example.com
  -u --userdata=DATA  User defined metadata string
  -F --userfile=FILE  Read userdata from file
"""
    action = 'edit'

    @staticmethod
    def execute(client, args):
        data = {}

        if args['--userdata'] and args['--userfile']:
            raise ArgumentError('[-u | --userdata] not allowed with '
                                '[-F | --userfile]')
        if args['--userfile']:
            if not os.path.exists(args['--userfile']):
                raise ArgumentError(
                    'File does not exist [-u | --userfile] = %s'
                    % args['--userfile'])

        if args.get('--userdata'):
            data['userdata'] = args['--userdata']
        elif args.get('--userfile'):
            f = open(args['--userfile'], 'r')
            try:
                data['userdata'] = f.read()
            finally:
                f.close()

        data['hostname'] = args.get('--hostname')
        data['domain'] = args.get('--domain')

        hw = HardwareManager(client)
        hw_id = resolve_id(hw.resolve_ids, args.get('<identifier>'),
                           'hardware')
        if not hw.edit(hw_id, **data):
            raise CLIAbort("Failed to update hardware")
