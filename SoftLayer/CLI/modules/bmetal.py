"""
usage: sl bmetal [<command>] [<args>...] [options]
       sl bmetal [-h | --help]

Manage bare metal instances

The available commands are:
  create-options  Output available available options when creating a server
  create    Create a new bare metal instance
  cancel    Cancels a bare metal instance

For several commands, <identifier> will be asked for. This can be the id,
hostname or the ip address for a piece of hardware.
"""
import re
from os import linesep
from SoftLayer.CLI import (
    CLIRunnable, Table, KeyValueTable, no_going_back, confirm, listing,
    FormattedItem)
from SoftLayer.CLI.helpers import (
    ArgumentError, CLIAbort, SequentialOutput, update_with_template_args,
    FALSE_VALUES, resolve_id)
from SoftLayer import HardwareManager


class BMetalCreateOptions(CLIRunnable):
    """
usage: sl bmetal create-options [options]

Output available available options when creating a bare metal instance.

Options:
  --all         Show all options. default if no other option provided
  --datacenter  Show datacenter options
  --cpu         Show CPU options
  --nic         Show NIC speed options
  --disk        Show disk options
  --os          Show operating system options
  --memory      Show memory size options
"""
    action = 'create-options'
    options = ['datacenter', 'cpu', 'memory', 'os', 'disk', 'nic']

    @classmethod
    def execute(cls, client, args):
        t = KeyValueTable(['Name', 'Value'])
        t.align['Name'] = 'r'
        t.align['Value'] = 'l'

        show_all = True
        for opt_name in cls.options:
            if args.get("--" + opt_name):
                show_all = False
                break

        mgr = HardwareManager(client)

        bmi_options = mgr.get_bare_metal_create_options()

        if args['--all']:
            show_all = True

        if args['--datacenter'] or show_all:
            results = cls.get_create_options(bmi_options, 'datacenter')[0]

            t.add_row([results[0], listing(sorted(results[1]))])

        if args['--cpu'] or args['--memory'] or show_all:
            results = cls.get_create_options(bmi_options, 'cpu')
            memory_cpu_table = Table(['memory', 'cpu'])
            for result in results:
                memory_cpu_table.add_row([
                    result[0],
                    listing(
                        [item[0] for item in sorted(
                            result[1], key=lambda x: int(x[0])
                        )])])
            t.add_row(['memory/cpu', memory_cpu_table])

        if args['--os'] or show_all:
            results = cls.get_create_options(bmi_options, 'os')

            for result in results:
                t.add_row([
                    result[0],
                    listing(
                        [item[0] for item in sorted(result[1])],
                        separator=linesep
                    )])

        if args['--disk'] or show_all:
            results = cls.get_create_options(bmi_options, 'disk')[0]

            t.add_row([results[0], listing(
                [item[0] for item in sorted(results[1])])])

        if args['--nic'] or show_all:
            results = cls.get_create_options(bmi_options, 'nic')

            for result in results:
                t.add_row([result[0], listing(
                    [item[0] for item in sorted(result[1],)])])

        return t

    @classmethod
    def get_create_options(cls, bmi_options, section, pretty=True):
        """ This method can be used to parse the bare metal instance creation
        options into different sections. This can be useful for data validation
        as well as printing the options on a help screen.

        :param dict bmi_options: The instance options to parse. Must come from
                                 the .get_bare_metal_create_options() function
                                 in the HardwareManager.
        :param string section: The section to parse out.
        :param bool pretty: If true, it will return the results in a 'pretty'
                            format that's easier to print.
        """
        if 'datacenter' == section:
            datacenters = [loc['keyname']
                           for loc in bmi_options['locations']]
            return [('datacenter', datacenters)]
        elif 'cpu' == section or 'memory' == section:
            mem_options = {}
            cpu_regex = re.compile('(\d+) x ')
            memory_regex = re.compile(' - (\d+) GB Ram', re.I)

            for item in bmi_options['categories']['server_core']['items']:
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

            return results
        elif 'os' == section:
            os_regex = re.compile('(^[A-Za-z\s\/]+) ([\d\.]+)')
            bit_regex = re.compile(' \((\d+)\s*bit')
            extra_regex = re.compile(' - (.+)\(')

            # Encapsulate the code for generating the operating system code
            def _generate_os_code(name, version, bits, extra_info):
                name = name.replace(' Linux', '')
                name = name.replace('Enterprise', '')
                name = name.replace('GNU/Linux', '')

                os_code = name.strip().replace(' ', '_').upper()

                if os_code == 'RED_HAT':
                    os_code = 'REDHAT'

                if 'UBUNTU' in os_code:
                    version = re.sub('\.\d+', '', version)

                os_code += '_' + version.replace('.0', '')

                if bits:
                    os_code += '_' + bits

                if extra_info:
                    os_code += '_' + extra_info.strip() \
                                               .replace(' Install', '').upper()

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

            for os in bmi_options['categories']['os']['items']:
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
            for disk in bmi_options['categories']['disk0']['items']:
                disks.append((int(disk['capacity']), disk['price_id']))

            return [('disks', disks)]
        elif 'nic' == section:
            single = []
            dual = []

            for item in bmi_options['categories']['port_speed']['items']:
                if 'dual' in item['description'].lower():
                    dual.append((str(int(item['capacity'])) + '_DUAL',
                                 item['price_id']))
                else:
                    single.append((int(item['capacity']), item['price_id']))

            return [('single nic', single), ('dual nic', dual)]

        return []


class CreateBMetalInstance(CLIRunnable):
    """
usage: sl bmetal create [--disk=DISK...] [options]

Order/create a bare metal instance. See 'sl bmetal create-options' for valid
options

Required:
  -H --hostname=HOST  Host portion of the FQDN. example: server
  -D --domain=DOMAIN  Domain portion of the FQDN example: example.com
  -c --cpu=CPU        Number of CPU cores
  -m --memory=MEMORY  Memory in mebibytes (n * 1024)

                      NOTE: Due to hardware configurations, the CPU and memory
                            must match appropriately. See create-options for
                            options.

  -o OS, --os=OS      OS install code.

  --hourly            Hourly rate instance type
  --monthly           Monthly rate instance type


Optional:
  -d DC, --datacenter=DC   datacenter name
                           Note: Omitting this value defaults to the first
                             available datacenter
  -n MBPS, --network=MBPS  Network port speed in Mbps
  --dry-run, --test        Do not create the instance, just get a quote
  -t, --template=FILE      A template file that defaults the command-line
                            options using the long name in INI format
  --export=FILE            Exports options to a template file
"""
    action = 'create'
    options = ['confirm']
    required_params = ['--hostname', '--domain', '--cpu', '--memory', '--os']

    @classmethod
    def execute(cls, client, args):
        update_with_template_args(args)
        mgr = HardwareManager(client)

        # Disks will be a comma-separated list. Let's make it a real list.
        if isinstance(args.get('--disk'), str):
            args['--disk'] = args.get('--disk').split(',')

        cls._validate_args(args)

        bmi_options = mgr.get_bare_metal_create_options()

        order = {
            'hostname': args['--hostname'],
            'domain': args['--domain'],
            'bare_metal': True,
        }

        # Validate the CPU/Memory combination and get the price ID
        server_core = cls._get_cpu_and_memory_price_ids(bmi_options,
                                                        args['--cpu'],
                                                        args['--memory'])

        if server_core:
            order['server'] = server_core
        else:
            raise CLIAbort('Invalid CPU/memory combination specified.')

        order['hourly'] = args['--hourly']

        # Convert the OS code back into a price ID
        os_price = cls._get_price_id_from_options(bmi_options, 'os',
                                                  args['--os'])

        if os_price:
            order['os'] = os_price
        else:
            raise CLIAbort('Invalid operating system specified.')

        order['location'] = args['--datacenter'] or 'FIRST_AVAILABLE'

        # Set the disk size
        disk_prices = []
        for disk in args.get('--disk'):
            disk_price = cls._get_price_id_from_options(bmi_options, 'disk',
                                                        disk)

            if disk_price:
                disk_prices.append(disk_price)

        if not disk_prices:
            disk_prices.append(cls._get_default_value(bmi_options, 'disk0'))

        order['disks'] = disk_prices

        # Set the port speed
        port_speed = args.get('--network') or 10

        nic_price = cls._get_price_id_from_options(bmi_options, 'nic',
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

            total_monthly = 0.0
            total_hourly = 0.0
            for price in result['prices']:
                total_monthly += float(price.get('recurringFee', 0.0))
                total_hourly += float(price.get('hourlyRecurringFee', 0.0))
                if args.get('--hourly'):
                    rate = "%.2f" % float(price['hourlyRecurringFee'])
                else:
                    rate = "%.2f" % float(price['recurringFee'])

                t.add_row([price['item']['description'], rate])

            if args.get('--hourly'):
                total = total_hourly
            else:
                total = total_monthly

            billing_rate = 'monthly'
            if args.get('--hourly'):
                billing_rate = 'hourly'
            t.add_row(['Total %s cost' % billing_rate, "%.2f" % total])
            output = SequentialOutput()
            output.append(t)
            output.append(FormattedItem(
                '',
                ' -- ! Prices reflected here are retail and do not '
                'take account level discounts and are not guarenteed.')
            )
        elif args['--really'] or confirm(
                "This action will incur charges on your account. Continue?"):
            result = mgr.place_order(**order)

            t = KeyValueTable(['name', 'value'])
            t.align['name'] = 'r'
            t.align['value'] = 'l'
            t.add_row(['id', result['orderId']])
            t.add_row(['created', result['orderDate']])
            output = t
        else:
            raise CLIAbort('Aborting bare metal instance order.')

        return output

    @classmethod
    def _validate_args(cls, args):
        invalid_args = [k for k in cls.required_params if args.get(k) is None]
        if invalid_args:
            raise ArgumentError('Missing required options: %s'
                                % ','.join(invalid_args))

        if args['--hourly'] in FALSE_VALUES:
            args['--hourly'] = False

        if args['--monthly'] in FALSE_VALUES:
            args['--monthly'] = False

        if all([args['--hourly'], args['--monthly']]):
            raise ArgumentError('[--hourly] not allowed with [--monthly]')

        if not any([args['--hourly'], args['--monthly']]):
            raise ArgumentError('One of [--hourly | --monthly] is required')

    @classmethod
    def _get_cpu_and_memory_price_ids(cls, bmi_options, cpu_value,
                                      memory_value):
        bmi_obj = BMetalCreateOptions()
        price_id = None

        cpu_regex = re.compile('(\d+)')
        for k, v in bmi_obj.get_create_options(bmi_options, 'cpu'):
            cpu = cpu_regex.search(k).group(1)

            if cpu == cpu_value:
                for mem_options in v:
                    if mem_options[0] == memory_value:
                        price_id = mem_options[1]

        return price_id

    @classmethod
    def _get_default_value(cls, bmi_options, option):
        if option not in bmi_options['categories']:
            return

        for item in bmi_options['categories'][option]['items']:
            if not any([
                    float(item.get('setupFee', 0)),
                    float(item.get('recurringFee', 0)),
                    float(item.get('hourlyRecurringFee', 0)),
                    float(item.get('oneTimeFee', 0)),
                    float(item.get('laborFee', 0)),
            ]):
                return item['price_id']

    @classmethod
    def _get_price_id_from_options(cls, bmi_options, option, value):
        bmi_obj = BMetalCreateOptions()
        price_id = None

        for k, v in bmi_obj.get_create_options(bmi_options, option, False):
            for item_options in v:
                if item_options[0] == value:
                    price_id = item_options[1]

        return price_id


class CancelInstance(CLIRunnable):
    """
usage: sl bmetal cancel <identifier> [options]

Cancel a bare metal instance

Options:
  --immediate  Cancels the instance immediately (instead of on the billing
                 anniversary).
"""

    action = 'cancel'
    options = ['confirm']

    @staticmethod
    def execute(client, args):
        hw = HardwareManager(client)
        hw_id = resolve_id(
            hw.resolve_ids, args.get('<identifier>'), 'hardware')

        immediate = args.get('--immediate', False)

        if args['--really'] or no_going_back(hw_id):
            hw.cancel_metal(hw_id, immediate)
        else:
            CLIAbort('Aborted')
