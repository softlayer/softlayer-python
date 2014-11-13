"""Hardware servers."""
import re


def get_create_options(ds_options, section, pretty=True):
    """Parse bare metal instance creation options.

    This method can be used to parse the bare metal instance creation
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
    elif ('server_core' == section
          and 'server_core' in ds_options['categories']):
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
                os_code = _generate_windows_code(opsys['description'])
            else:
                os_results = os_regex.search(opsys['description'])

                # Skip this operating system if it's not parsable
                if os_results is None:
                    continue

                name = os_results.group(1)
                version = os_results.group(2)
                bits = bit_regex.search(opsys['description'])
                extra_info = extra_regex.search(opsys['description'])

                if bits:
                    bits = bits.group(1)
                if extra_info:
                    extra_info = extra_info.group(1)

                os_code = _generate_os_code(name, version, bits, extra_info)

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


def _generate_os_code(name, version, bits, extra_info):
    """Encapsulates the code for generating the operating system code."""
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


def _generate_windows_code(description):
    """Generates OS codes for windows."""
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
