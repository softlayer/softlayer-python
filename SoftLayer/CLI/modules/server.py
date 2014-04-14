"""
usage: sl server [<command>] [<args>...] [options]
       sl server [-h | --help]

Manage hardware servers

The available commands are:
  cancel          Cancel a dedicated server.
  cancel-reasons  Provides the list of possible cancellation reasons
  create          Create a new dedicated server
  create-options  Display a list of creation options for a specific chassis
  detail          Retrieve hardware details
  list            List hardware devices
  list-chassis    Provide a list of all chassis available for ordering
  nic-edit        Edit NIC settings
  power-cycle     Issues power cycle to server
  power-off       Powers off a running server
  power-on        Boots up a server
  reboot          Reboots a running server
  reload          Perform an OS reload

For several commands, <identifier> will be asked for. This can be the id,
hostname or the ip address for a piece of hardware.
"""
# :license: MIT, see LICENSE for more details.
import re
import os
from os import linesep
from SoftLayer.CLI.helpers import (
    CLIRunnable, Table, KeyValueTable, FormattedItem, NestedDict, CLIAbort,
    blank, listing, gb, active_txn, no_going_back, resolve_id, confirm,
    ArgumentError, update_with_template_args, export_to_template)
from SoftLayer import HardwareManager, SshKeyManager


class ListServers(CLIRunnable):
    """
usage: sl server list [options]

List hardware servers on the acount

Examples:
  sl server list --datacenter=dal05
  sl server list --network=100 --domain=example.com
  sl server list --tags=production,db

Options:
  --sortby=ARG  Column to sort by. options: id, datacenter, host, cores,
                  memory, primary_ip, backend_ip

Filters:
  -c, --cpu=CPU        Number of CPU cores
  -D, --domain=DOMAIN  Domain portion of the FQDN. example: example.com
  -d, --datacenter=DC  Datacenter shortname (sng01, dal05, ...)
  -H, --hostname=HOST  Host portion of the FQDN. example: server
  -m, --memory=MEMORY  Memory in gigabytes
  -n, --network=MBPS   Network port speed in Mbps
  --tags=ARG           Only show instances that have one of these tags.
                         Comma-separated. (production,db)

For more on filters see 'sl help filters'
"""
    action = 'list'

    def execute(self, args):
        manager = HardwareManager(self.client)

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

        table = Table([
            'id',
            'datacenter',
            'host',
            'cores',
            'memory',
            'primary_ip',
            'backend_ip',
            'active_transaction'
        ])
        table.sortby = args.get('--sortby') or 'host'

        for server in servers:
            server = NestedDict(server)
            table.add_row([
                server['id'],
                server['datacenter']['name'] or blank(),
                server['fullyQualifiedDomainName'],
                server['processorPhysicalCoreAmount'],
                gb(server['memoryCapacity'] or 0),
                server['primaryIpAddress'] or blank(),
                server['primaryBackendIpAddress'] or blank(),
                active_txn(server),
            ])

        return table


class ServerDetails(CLIRunnable):
    """
usage: sl server detail [--passwords] [--price] <identifier> [options]

Get details for a hardware device

Options:
  --passwords  Show passwords (check over your shoulder!)
  --price      Show associated prices
"""
    action = 'detail'

    def execute(self, args):
        hardware = HardwareManager(self.client)

        table = KeyValueTable(['Name', 'Value'])
        table.align['Name'] = 'r'
        table.align['Value'] = 'l'

        hardware_id = resolve_id(
            hardware.resolve_ids, args.get('<identifier>'), 'hardware')
        result = hardware.get_hardware(hardware_id)
        result = NestedDict(result)

        table.add_row(['id', result['id']])
        table.add_row(['hostname', result['fullyQualifiedDomainName']])
        table.add_row(['status', result['hardwareStatus']['status']])
        table.add_row(['datacenter', result['datacenter']['name'] or blank()])
        table.add_row(['cores', result['processorPhysicalCoreAmount']])
        table.add_row(['memory', gb(result['memoryCapacity'])])
        table.add_row(['public_ip', result['primaryIpAddress'] or blank()])
        table.add_row(
            ['private_ip', result['primaryBackendIpAddress'] or blank()])
        table.add_row(['ipmi_ip',
                       result['networkManagementIpAddress'] or blank()])
        table.add_row([
            'os',
            FormattedItem(
                result['operatingSystem']['softwareLicense']
                ['softwareDescription']['referenceCode'] or blank(),
                result['operatingSystem']['softwareLicense']
                ['softwareDescription']['name'] or blank()
            )])
        table.add_row(['created', result['provisionDate'] or blank()])

        vlan_table = Table(['type', 'number', 'id'])
        for vlan in result['networkVlans']:
            vlan_table.add_row([
                vlan['networkSpace'], vlan['vlanNumber'], vlan['id']])
        table.add_row(['vlans', vlan_table])

        if result.get('notes'):
            table.add_row(['notes', result['notes']])

        if args.get('--price'):
            table.add_row(['price rate',
                           result['billingItem']['recurringFee']])

        if args.get('--passwords'):
            user_strs = []
            for item in result['operatingSystem']['passwords']:
                user_strs.append(
                    "%s %s" % (item['username'], item['password']))
            table.add_row(['users', listing(user_strs)])

        tag_row = []
        for tag in result['tagReferences']:
            tag_row.append(tag['tag']['name'])

        if tag_row:
            table.add_row(['tags', listing(tag_row, separator=',')])

        if not result['privateNetworkOnlyFlag']:
            ptr_domains = self.client['Hardware_Server']\
                .getReverseDomainRecords(id=hardware_id)

            for ptr_domain in ptr_domains:
                for ptr in ptr_domain['resourceRecords']:
                    table.add_row(['ptr', ptr['data']])

        return table


class ServerReload(CLIRunnable):
    """
usage: sl server reload <identifier> [--key=KEY...] [options]

Reload the OS on a hardware server based on its current configuration

Optional:
  -i, --postinstall=URI  Post-install script to download
                           (Only HTTPS executes, HTTP leaves file in /root)
  -k, --key=KEY          SSH keys to add to the root user. Can be specified
                           multiple times
"""

    action = 'reload'
    options = ['confirm']

    def execute(self, args):
        hardware = HardwareManager(self.client)
        hardware_id = resolve_id(
            hardware.resolve_ids, args.get('<identifier>'), 'hardware')
        keys = []
        if args.get('--key'):
            for key in args.get('--key'):
                key_id = resolve_id(SshKeyManager(self.client).resolve_ids,
                                    key, 'SshKey')
                keys.append(key_id)
        if args['--really'] or no_going_back(hardware_id):
            hardware.reload(hardware_id, args['--postinstall'], keys)
        else:
            CLIAbort('Aborted')


class CancelServer(CLIRunnable):
    """
usage: sl server cancel <identifier> [options]

Cancel a dedicated server

Options:
  --comment=COMMENT  An optional comment to add to the cancellation ticket
  --reason=REASON    An optional cancellation reason. See cancel-reasons for a
                       list of available options
"""

    action = 'cancel'
    options = ['confirm']

    def execute(self, args):
        mgr = HardwareManager(self.client)
        hw_id = resolve_id(
            mgr.resolve_ids, args.get('<identifier>'), 'hardware')

        comment = args.get('--comment')

        if not comment and not args['--really']:
            comment = self.env.input("(Optional) Add a cancellation comment:")

        reason = args.get('--reason')

        if args['--really'] or no_going_back(hw_id):
            mgr.cancel_hardware(hw_id, reason, comment)
        else:
            CLIAbort('Aborted')


class ServerCancelReasons(CLIRunnable):
    """
usage: sl server cancel-reasons

Display a list of cancellation reasons
"""

    action = 'cancel-reasons'

    def execute(self, args):
        table = Table(['Code', 'Reason'])
        table.align['Code'] = 'r'
        table.align['Reason'] = 'l'

        mgr = HardwareManager(self.client)

        for code, reason in mgr.get_cancellation_reasons().items():
            table.add_row([code, reason])

        return table


class ServerPowerOff(CLIRunnable):
    """
usage: sl server power-off <identifier> [options]

Power off an active server
"""
    action = 'power-off'
    options = ['confirm']

    def execute(self, args):
        mgr = HardwareManager(self.client)
        hw_id = resolve_id(mgr.resolve_ids, args.get('<identifier>'),
                           'hardware')
        if args['--really'] or confirm('This will power off the server with '
                                       'id %s. Continue?' % hw_id):
            self.client['Hardware_Server'].powerOff(id=hw_id)
        else:
            raise CLIAbort('Aborted.')


class ServerReboot(CLIRunnable):
    """
usage: sl server reboot <identifier> [--hard | --soft] [options]

Reboot an active server

Optional:
    --hard  Perform an abrupt reboot
    --soft  Perform a graceful reboot
"""
    action = 'reboot'
    options = ['confirm']

    def execute(self, args):
        hardware_server = self.client['Hardware_Server']
        mgr = HardwareManager(self.client)
        hw_id = resolve_id(mgr.resolve_ids, args.get('<identifier>'),
                           'hardware')
        if args['--really'] or confirm('This will power off the server with '
                                       'id %s. Continue?' % hw_id):
            if args['--hard']:
                hardware_server.rebootHard(id=hw_id)
            elif args['--soft']:
                hardware_server.rebootSoft(id=hw_id)
            else:
                hardware_server.rebootDefault(id=hw_id)
        else:
            raise CLIAbort('Aborted.')


class ServerPowerOn(CLIRunnable):
    """
usage: sl server power-on <identifier> [options]

Power on a server
"""
    action = 'power-on'

    def execute(self, args):
        mgr = HardwareManager(self.client)
        hw_id = resolve_id(mgr.resolve_ids, args.get('<identifier>'),
                           'hardware')
        self.client['Hardware_Server'].powerOn(id=hw_id)


class ServerPowerCycle(CLIRunnable):
    """
usage: sl server power-cycle <identifier> [options]

Issues power cycle to server via the power strip
"""
    action = 'power-cycle'
    options = ['confirm']

    def execute(self, args):
        mgr = HardwareManager(self.client)
        hw_id = resolve_id(mgr.resolve_ids, args.get('<identifier>'),
                           'hardware')

        if args['--really'] or confirm('This will power off the server with '
                                       'id %s. Continue?' % hw_id):
            self.client['Hardware_Server'].powerCycle(id=hw_id)
        else:
            raise CLIAbort('Aborted.')


class NicEditServer(CLIRunnable):
    """
usage: sl server nic-edit <identifier> (public | private) --speed=SPEED
                          [options]

Manage NIC settings

Options:
    --speed=SPEED  Port speed. 0 disables the port.
                     [Options: 0, 10, 100, 1000, 10000]
"""
    action = 'nic-edit'

    def execute(self, args):
        public = args['public']

        mgr = HardwareManager(self.client)
        hw_id = resolve_id(mgr.resolve_ids, args.get('<identifier>'),
                           'hardware')

        mgr.change_port_speed(hw_id, public, args['--speed'])


class ListChassisServer(CLIRunnable):
    """
usage: sl server list-chassis [options]

Display a list of chassis available for ordering dedicated servers.
"""
    action = 'list-chassis'

    def execute(self, args):
        table = Table(['Code', 'Chassis'])
        table.align['Code'] = 'r'
        table.align['Chassis'] = 'l'

        mgr = HardwareManager(self.client)
        chassis = mgr.get_available_dedicated_server_packages()

        for chassis in chassis:
            table.add_row([chassis[0], chassis[1]])

        return table


class ServerCreateOptions(CLIRunnable):
    """
usage: sl server create-options <chassis_id> [options]

Output available available options when creating a dedicated server with the
specified chassis.

Options:
  --all         Show all options. default if no other option provided
  --controller  Show disk controller options
  --cpu         Show CPU options
  --datacenter  Show datacenter options
  --disk        Show disk options
  --memory      Show memory size options
  --nic         Show NIC speed options
  --os          Show operating system options
"""

    action = 'create-options'
    options = ['datacenter', 'cpu', 'memory', 'os', 'disk', 'nic',
               'controller']

    def execute(self, args):
        mgr = HardwareManager(self.client)

        table = KeyValueTable(['Name', 'Value'])
        table.align['Name'] = 'r'
        table.align['Value'] = 'l'

        chassis_id = args.get('<chassis_id>')

        found = False
        for chassis in mgr.get_available_dedicated_server_packages():
            if chassis_id == str(chassis[0]):
                found = True
                break

        if not found:
            raise CLIAbort('Invalid chassis specified.')

        ds_options = mgr.get_dedicated_server_create_options(chassis_id)

        show_all = True
        for opt_name in self.options:
            if args.get("--" + opt_name):
                show_all = False
                break

        if args['--all']:
            show_all = True

        # Determine if this is a "Bare Metal Instance" or regular server
        bmc = False
        if chassis_id == str(mgr.get_bare_metal_package_id()):
            bmc = True

        if args['--datacenter'] or show_all:
            results = self.get_create_options(ds_options, 'datacenter')[0]

            table.add_row([results[0], listing(sorted(results[1]))])

        if (args['--cpu'] or show_all) and not bmc:
            results = self.get_create_options(ds_options, 'cpu')

            cpu_table = Table(['ID', 'Description'])
            cpu_table.align['ID'] = 'r'
            cpu_table.align['Description'] = 'l'

            for result in sorted(results, key=lambda x: x[1]):
                cpu_table.add_row([result[1], result[0]])
            table.add_row(['cpu', cpu_table])

        if (args['--memory'] or show_all) and not bmc:
            results = self.get_create_options(ds_options, 'memory')[0]

            table.add_row([results[0], listing(
                item[0] for item in sorted(results[1]))])

        if bmc and (show_all or args['--memory'] or args['--cpu']):
            results = self.get_create_options(ds_options, 'server_core')
            memory_cpu_table = Table(['memory', 'cpu'])
            for result in results:
                memory_cpu_table.add_row([
                    result[0],
                    listing(
                        [item[0] for item in sorted(
                            result[1], key=lambda x: int(x[0])
                        )])])
            table.add_row(['memory/cpu', memory_cpu_table])

        if args['--os'] or show_all:
            results = self.get_create_options(ds_options, 'os')

            for result in results:
                table.add_row([
                    result[0],
                    listing(
                        [item[0] for item in sorted(result[1])],
                        separator=linesep
                    )])

        if args['--disk'] or show_all:
            results = self.get_create_options(ds_options, 'disk')[0]

            table.add_row([
                results[0],
                listing(
                    [item[0] for item in sorted(results[1])],
                    separator=linesep
                )])

        if args['--nic'] or show_all:
            results = self.get_create_options(ds_options, 'nic')

            for result in results:
                table.add_row([result[0], listing(
                    item[0] for item in sorted(result[1],))])

        if (args['--controller'] or show_all) and not bmc:
            results = self.get_create_options(ds_options, 'disk_controller')[0]

            table.add_row([results[0], listing(
                item[0] for item in sorted(results[1],))])

        return table

    def get_create_options(self, ds_options, section, pretty=True):
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
        return_value = None

        if 'datacenter' == section:
            datacenters = [loc['keyname']
                           for loc in ds_options['locations']]
            return_value = [('datacenter', datacenters)]
        elif 'cpu' == section and 'server' in ds_options['categories']:
            results = []

            for item in ds_options['categories']['server']['items']:
                results.append((
                    item['description'],
                    item['price_id']
                ))

            return_value = results
        elif 'memory' == section and 'ram' in ds_options['categories']:
            ram = []
            for option in ds_options['categories']['ram']['items']:
                ram.append((int(option['capacity']), option['price_id']))

            return_value = [('memory', ram)]
        elif 'server_core' == section and \
             'server_core' in ds_options['categories']:
            mem_options = {}
            cpu_regex = re.compile(r'(\d+) x ')
            memory_regex = re.compile(r' - (\d+) GB Ram', re.I)

            for item in ds_options['categories']['server_core']['items']:
                cpu = cpu_regex.search(item['description']).group(1)
                memory = memory_regex.search(item['description']).group(1)

                if cpu and memory:
                    if memory not in mem_options:
                        mem_options[memory] = []

                    mem_options[memory].append((cpu, item['price_id']))

            results = []
            for memory in sorted(mem_options.keys(), key=int):
                key = memory

                if pretty:
                    key = memory

                results.append((key, mem_options[memory]))

            return_value = results
        elif 'os' == section:
            os_regex = re.compile(r'(^[A-Za-z\s\/\-]+) ([\d\.]+)')
            bit_regex = re.compile(r' \((\d+)\s*bit')
            extra_regex = re.compile(r' - (.+)\(')

            os_list = {}
            flat_list = []

            # Loop through the operating systems and get their OS codes
            for opsys in ds_options['categories']['os']['items']:
                if 'Windows Server' in opsys['description']:
                    os_code = self._generate_windows_code(opsys['description'])
                else:
                    os_results = os_regex.search(opsys['description'])
                    name = os_results.group(1)
                    version = os_results.group(2)
                    bits = bit_regex.search(opsys['description'])
                    extra_info = extra_regex.search(opsys['description'])

                    if bits:
                        bits = bits.group(1)
                    if extra_info:
                        extra_info = extra_info.group(1)

                    os_code = self._generate_os_code(name, version, bits,
                                                     extra_info)

                name = os_code.split('_')[0]

                if name not in os_list:
                    os_list[name] = []

                os_list[name].append((os_code, opsys['price_id']))
                flat_list.append((os_code, opsys['price_id']))

            if pretty:
                results = []
                for opsys in sorted(os_list.keys()):
                    results.append(('os (%s)' % opsys, os_list[opsys]))

                return_value = results
            else:
                return_value = [('os', flat_list)]

        elif 'disk' == section:
            disks = []
            type_regex = re.compile(r'^[\d\.]+[GT]B\s+(.+)$')
            for disk in ds_options['categories']['disk0']['items']:
                disk_type = 'SATA'
                disk_type = type_regex.match(disk['description']).group(1)

                disk_type = disk_type.replace('RPM', '').strip()
                disk_type = disk_type.replace(' ', '_').upper()
                disk_type = str(int(disk['capacity'])) + '_' + disk_type
                disks.append((disk_type, disk['price_id'], disk['id']))

            return_value = [('disk', disks)]
        elif 'nic' == section:
            single = []
            dual = []

            for item in ds_options['categories']['port_speed']['items']:
                if 'dual' in item['description'].lower():
                    dual.append((str(int(item['capacity'])) + '_DUAL',
                                 item['price_id']))
                else:
                    single.append((str(int(item['capacity'])),
                                   item['price_id']))

            return_value = [('single nic', single), ('dual nic', dual)]
        elif 'disk_controller' == section:
            options = []
            for item in ds_options['categories']['disk_controller']['items']:
                text = item['description'].replace(' ', '')

                if 'Non-RAID' == text:
                    text = 'None'

                options.append((text, item['price_id']))

            return_value = [('disk_controllers', options)]

        return return_value

    def _generate_os_code(self, name, version, bits, extra_info):
        """ Encapsulates the code for generating the operating system code. """
        name = name.replace(' Linux', '')
        name = name.replace('Enterprise', '')
        name = name.replace('GNU/Linux', '')

        os_code = name.strip().replace(' ', '_').upper()

        if os_code.startswith('RED_HAT'):
            os_code = 'REDHAT'

        if 'UBUNTU' in os_code:
            version = re.sub(r'\.\d+', '', version)

        os_code += '_' + version.replace('.0', '')

        if bits:
            os_code += '_' + bits

        if extra_info:
            garbage = ['Install', '(32 bit)', '(64 bit)']

            for obj in garbage:
                extra_info = extra_info.replace(obj, '')

            os_code += '_' + extra_info.strip().replace(' ', '_').upper()

        return os_code

    def _generate_windows_code(self, description):
        """ Separates the code for generating the Windows OS code
        since it's significantly different from the rest.
        """
        version_check = re.search(r'Windows Server (\d+)', description)
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

        bit_check = re.search(r'\((\d+)\s*bit', description)
        if bit_check:
            os_code += '_' + bit_check.group(1)

        return os_code


class CreateServer(CLIRunnable):
    """
usage: sl server create [--disk=SIZE...] [--key=KEY...] [options]

Order/create a dedicated server. See 'sl server list-chassis' and
'sl server create-options' for valid options.

Required:
  -H --hostname=HOST  Host portion of the FQDN. example: server
  -D --domain=DOMAIN  Domain portion of the FQDN. example: example.com
  --chassis=CHASSIS   The chassis to use for the new server
  -c --cpu=CPU        CPU model
  -o OS, --os=OS      OS install code.
  -m --memory=MEMORY  Memory in gigabytes. example: 4
  --billing=BILLING   Billing rate. Options are "monthly" (default) or
                        "hourly". The hourly rate is only available on the
                        "Bare Metal Instance" chassis.

Optional:
  -d, --datacenter=DC    Datacenter name
                           Note: Omitting this value defaults to the first
                           available datacenter
  -n, --network=MBPS     Network port speed in Mbps
  --disk=SIZE...         Disks. Can be specified multiple times
  --controller=RAID      The RAID configuration for the server.
                           Defaults to None.
  -i, --postinstall=URI  Post-install script to download
  -k KEY, --key=KEY      SSH keys to assign to the root user. Can be specified
                           multiple times.
  --dry-run, --test      Do not create the server, just get a quote
  --vlan_public=VLAN     The ID of the public VLAN on which you want the
                           hardware placed
  --vlan_private=VLAN    The ID of the private VLAN on which you want the
                           hardware placed
  -t, --template=FILE    A template file that defaults the command-line
                           options using the long name in INI format
  --export=FILE          Exports options to a template file
"""
    action = 'create'
    options = ['confirm']
    required_params = ['--hostname', '--domain', '--chassis', '--cpu',
                       '--memory', '--os']

    def execute(self, args):
        update_with_template_args(args)
        mgr = HardwareManager(self.client)

        # Disks will be a comma-separated list. Let's make it a real list.
        if isinstance(args.get('--disk'), str):
            args['--disk'] = args.get('--disk').split(',')

        # Do the same thing for SSH keys
        if isinstance(args.get('--key'), str):
            args['--key'] = args.get('--key').split(',')

        self._validate_args(args)

        ds_options = mgr.get_dedicated_server_create_options(args['--chassis'])

        order = self._process_args(args, ds_options)

        # Do not create hardware server with --test or --export
        do_create = not (args['--export'] or args['--test'])

        output = None
        if args.get('--test'):
            result = mgr.verify_order(**order)

            table = Table(['Item', 'cost'])
            table.align['Item'] = 'r'
            table.align['cost'] = 'r'

            total = 0.0
            for price in result['prices']:
                total += float(price.get('recurringFee', 0.0))
                rate = "%.2f" % float(price['recurringFee'])

                table.add_row([price['item']['description'], rate])

            table.add_row(['Total monthly cost', "%.2f" % total])
            output = []
            output.append(table)
            output.append(FormattedItem(
                '',
                ' -- ! Prices reflected here are retail and do not '
                'take account level discounts and are not guaranteed.')
            )

        if args['--export']:
            export_file = args.pop('--export')
            export_to_template(export_file, args, exclude=['--wait', '--test'])
            return 'Successfully exported options to a template file.'

        if do_create:
            if args['--really'] or confirm(
                    "This action will incur charges on your account. "
                    "Continue?"):
                result = mgr.place_order(**order)

                table = KeyValueTable(['name', 'value'])
                table.align['name'] = 'r'
                table.align['value'] = 'l'
                table.add_row(['id', result['orderId']])
                table.add_row(['created', result['orderDate']])
                output = table
            else:
                raise CLIAbort('Aborting dedicated server order.')

        return output

    def _process_args(self, args, ds_options):
        """
        Helper method to centralize argument processing without convoluting
        code flow of the main execute method.
        """
        mgr = HardwareManager(self.client)

        order = {
            'hostname': args['--hostname'],
            'domain': args['--domain'],
            'bare_metal': False,
            'package_id': args['--chassis'],
        }

        # Determine if this is a "Bare Metal Instance" or regular server
        bmc = False
        if args['--chassis'] == str(mgr.get_bare_metal_package_id()):
            bmc = True

        # Convert the OS code back into a price ID
        os_price = self._get_price_id_from_options(ds_options, 'os',
                                                   args['--os'])

        if os_price:
            order['os'] = os_price
        else:
            raise CLIAbort('Invalid operating system specified.')

        order['location'] = args['--datacenter'] or 'FIRST_AVAILABLE'

        if bmc:
            order['server'] = self._get_cpu_and_memory_price_ids(
                ds_options, args['--cpu'], args['--memory'])
            order['bare_metal'] = True

            if args['--billing'] == 'hourly':
                order['hourly'] = True
        else:
            order['server'] = args['--cpu']
            order['ram'] = self._get_price_id_from_options(
                ds_options, 'memory', int(args['--memory']))

        # Set the disk sizes
        disk_prices = []
        disk_number = 0
        for disk in args.get('--disk'):
            disk_price = self._get_disk_price(ds_options, disk, disk_number)
            disk_number += 1
            if disk_price:
                disk_prices.append(disk_price)

        if not disk_prices:
            disk_prices.append(self._get_default_value(ds_options, 'disk0'))

        order['disks'] = disk_prices

        # Set the disk controller price
        if not bmc:
            if args.get('--controller'):
                dc_price = self._get_price_id_from_options(
                    ds_options, 'disk_controller', args.get('--controller'))
            else:
                dc_price = self._get_price_id_from_options(ds_options,
                                                           'disk_controller',
                                                           'None')

            order['disk_controller'] = dc_price

        # Set the port speed
        port_speed = args.get('--network') or '100'

        nic_price = self._get_price_id_from_options(ds_options, 'nic',
                                                    port_speed)

        if nic_price:
            order['port_speed'] = nic_price
        else:
            raise CLIAbort('Invalid NIC speed specified.')

        if args.get('--postinstall'):
            order['post_uri'] = args.get('--postinstall')

        # Get the SSH keys
        if args.get('--key'):
            keys = []
            for key in args.get('--key'):
                key_id = resolve_id(SshKeyManager(self.client).resolve_ids,
                                    key, 'SshKey')
                keys.append(key_id)
            order['ssh_keys'] = keys

        if args.get('--vlan_public'):
            order['public_vlan'] = args['--vlan_public']

        if args.get('--vlan_private'):
            order['private_vlan'] = args['--vlan_private']

        return order

    def _validate_args(self, args):
        """ Raises an ArgumentError if the given arguments are not valid """
        invalid_args = [k for k in self.required_params if args.get(k) is None]
        if invalid_args:
            raise ArgumentError('Missing required options: %s'
                                % ','.join(invalid_args))

    def _get_default_value(self, ds_options, option):
        """ Returns a 'free' price id given an option """
        if option not in ds_options['categories']:
            return

        for item in ds_options['categories'][option]['items']:
            if not any([
                    float(item.get('setupFee', 0)),
                    float(item.get('recurringFee', 0)),
                    float(item.get('hourlyRecurringFee', 0)),
                    float(item.get('oneTimeFee', 0)),
                    float(item.get('laborFee', 0)),
            ]):
                return item['price_id']

    def _get_disk_price(self, ds_options, value, number):
        """ Returns a price id that matches a given disk config """
        if not number:
            return self._get_price_id_from_options(ds_options, 'disk', value)
        # This will get the item ID for the matching identifier string, which
        # we can then use to get the price ID for our specific disk
        item_id = self._get_price_id_from_options(ds_options, 'disk',
                                                  value, True)
        key = 'disk' + str(number)
        if key in ds_options['categories']:
            for item in ds_options['categories'][key]['items']:
                if item['id'] == item_id:
                    return item['price_id']

    def _get_cpu_and_memory_price_ids(self, ds_options, cpu_value,
                                      memory_value):
        """
        Returns a price id for a cpu/memory pair in pre-configured servers
        (formerly known as BMC).
        """
        ds_obj = ServerCreateOptions()
        for memory, options in ds_obj.get_create_options(ds_options,
                                                         'server_core',
                                                         False):
            if memory == memory_value:
                for cpu_size, price_id in options:
                    if cpu_size == cpu_value:
                        return price_id

    def _get_price_id_from_options(self, ds_options, option, value,
                                   item_id=False):
        """ Returns a price_id for a given option and value """
        ds_obj = ServerCreateOptions()

        for _, options in ds_obj.get_create_options(ds_options, option, False):
            for item_options in options:
                if item_options[0] == value:
                    if not item_id:
                        return item_options[1]
                    return item_options[2]


class EditServer(CLIRunnable):
    """
usage: sl server edit <identifier> [options]

Edit hardware details

Options:
  -D --domain=DOMAIN  Domain portion of the FQDN example: example.com
  -F --userfile=FILE  Read userdata from file
  -H --hostname=HOST  Host portion of the FQDN. example: server
  -u --userdata=DATA  User defined metadata string
"""
    action = 'edit'

    def execute(self, args):
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
            with open(args['--userfile'], 'r') as userfile:
                data['userdata'] = userfile.read()

        data['hostname'] = args.get('--hostname')
        data['domain'] = args.get('--domain')

        mgr = HardwareManager(self.client)
        hw_id = resolve_id(mgr.resolve_ids, args.get('<identifier>'),
                           'hardware')
        if not mgr.edit(hw_id, **data):
            raise CLIAbort("Failed to update hardware")
