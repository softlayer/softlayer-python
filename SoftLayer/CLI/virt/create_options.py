"""Virtual server order options."""
# :license: MIT, see LICENSE for more details.
# pylint: disable=too-many-statements
import os
import os.path

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer import utils


@click.command(short_help="Get options to use for creating virtual servers.")
@environment.pass_env
def cli(env):
    """Virtual server order options."""

    vsi = SoftLayer.VSManager(env.client)
    options = vsi.get_create_options()

    tables = [
        _get_datacenter_table(options),
        _get_flavors_table(options),
        _get_cpu_table(options),
        _get_memory_table(options),
        _get_os_table(options),
        _get_disk_table(options),
        _get_network_table(options),
    ]

    env.fout(formatting.listing(tables, separator='\n'))


def _get_datacenter_table(create_options):
    datacenters = [dc['template']['datacenter']['name']
                   for dc in create_options['datacenters']]

    datacenters = sorted(datacenters)

    dc_table = formatting.Table(['datacenter'], title='Datacenters')
    dc_table.sortby = 'datacenter'
    dc_table.align = 'l'
    for datacenter in datacenters:
        dc_table.add_row([datacenter])
    return dc_table


def _get_flavors_table(create_options):
    flavor_table = formatting.Table(['flavor', 'value'], title='Flavors')
    flavor_table.sortby = 'flavor'
    flavor_table.align = 'l'
    grouping = {
        'balanced': {'key_starts_with': 'B1', 'flavors': []},
        'balanced local - hdd': {'key_starts_with': 'BL1', 'flavors': []},
        'balanced local - ssd': {'key_starts_with': 'BL2', 'flavors': []},
        'compute': {'key_starts_with': 'C1', 'flavors': []},
        'memory': {'key_starts_with': 'M1', 'flavors': []},
        'GPU': {'key_starts_with': 'AC', 'flavors': []},
        'transient': {'transient': True, 'flavors': []},
    }

    if create_options.get('flavors', None) is None:
        return

    for flavor_option in create_options['flavors']:
        flavor_key_name = utils.lookup(flavor_option, 'flavor', 'keyName')

        for name, group in grouping.items():
            if utils.lookup(flavor_option, 'template', 'transientGuestFlag') is True:
                if utils.lookup(group, 'transient') is True:
                    group['flavors'].append(flavor_key_name)
                    break

            elif utils.lookup(group, 'key_starts_with') is not None \
                    and flavor_key_name.startswith(group['key_starts_with']):
                group['flavors'].append(flavor_key_name)
                break

    for name, group in grouping.items():
        if len(group['flavors']) > 0:
            flavor_table.add_row(['{}'.format(name),
                                  formatting.listing(group['flavors'],
                                                     separator='\n')])
    return flavor_table


def _get_cpu_table(create_options):
    cpu_table = formatting.Table(['cpu', 'value'], title='CPUs')
    cpu_table.sortby = 'cpu'
    cpu_table.align = 'l'
    standard_cpus = [int(x['template']['startCpus']) for x in create_options['processors']
                     if not x['template'].get('dedicatedAccountHostOnlyFlag',
                                              False)
                     and not x['template'].get('dedicatedHost', None)]
    ded_cpus = [int(x['template']['startCpus']) for x in create_options['processors']
                if x['template'].get('dedicatedAccountHostOnlyFlag', False)]
    ded_host_cpus = [int(x['template']['startCpus']) for x in create_options['processors']
                     if x['template'].get('dedicatedHost', None)]

    standard_cpus = sorted(standard_cpus)
    cpu_table.add_row(['standard', formatting.listing(standard_cpus, separator=',')])
    ded_cpus = sorted(ded_cpus)
    cpu_table.add_row(['dedicated', formatting.listing(ded_cpus, separator=',')])
    ded_host_cpus = sorted(ded_host_cpus)
    cpu_table.add_row(['dedicated host', formatting.listing(ded_host_cpus, separator=',')])
    return cpu_table


def _get_memory_table(create_options):
    memory_table = formatting.Table(['memory', 'value'], title='Memories')
    memory_table.sortby = 'memory'
    memory_table.align = 'l'
    memory = [int(m['template']['maxMemory']) for m in create_options['memory']
              if not m['itemPrice'].get('dedicatedHostInstanceFlag', False)]
    ded_host_memory = [int(m['template']['maxMemory']) for m in create_options['memory']
                       if m['itemPrice'].get('dedicatedHostInstanceFlag', False)]

    memory = sorted(memory)
    memory_table.add_row(['standard',
                          formatting.listing(memory, separator=',')])

    ded_host_memory = sorted(ded_host_memory)
    memory_table.add_row(['dedicated host',
                          formatting.listing(ded_host_memory, separator=',')])
    return memory_table


def _get_os_table(create_options):
    os_table = formatting.Table(['os', 'value'], title='Operating Systems')
    os_table.sortby = 'os'
    os_table.align = 'l'
    op_sys = [o['template']['operatingSystemReferenceCode'] for o in
              create_options['operatingSystems']]

    op_sys = sorted(op_sys)
    os_summary = set()

    for operating_system in op_sys:
        os_summary.add(operating_system[0:operating_system.find('_')])

    for summary in sorted(os_summary):
        os_table.add_row([
            summary,
            os.linesep.join(sorted([x for x in op_sys
                                    if x[0:len(summary)] == summary]))
        ])
    return os_table


def _get_disk_table(create_options):
    disk_table = formatting.Table(['disk', 'value'], title='Disks')
    disk_table.sortby = 'disk'
    disk_table.align = 'l'
    local_disks = [x for x in create_options['blockDevices']
                   if x['template'].get('localDiskFlag', False)
                   and not x['itemPrice'].get('dedicatedHostInstanceFlag',
                                              False)]

    ded_host_local_disks = [x for x in create_options['blockDevices']
                            if x['template'].get('localDiskFlag', False)
                            and x['itemPrice'].get('dedicatedHostInstanceFlag',
                                                   False)]

    san_disks = [x for x in create_options['blockDevices']
                 if not x['template'].get('localDiskFlag', False)]

    def add_block_rows(disks, name):
        """Add block rows to the table."""
        simple = {}
        for disk in disks:
            block = disk['template']['blockDevices'][0]
            bid = block['device']

            if bid not in simple:
                simple[bid] = []

            simple[bid].append(str(block['diskImage']['capacity']))

        for label in sorted(simple):
            disk_table.add_row(['%s disk(%s)' % (name, label),
                                formatting.listing(simple[label],
                                                   separator=',')])

    add_block_rows(san_disks, 'san')
    add_block_rows(local_disks, 'local')
    add_block_rows(ded_host_local_disks, 'local (dedicated host)')
    return disk_table


def _get_network_table(create_options):
    network_table = formatting.Table(['network', 'value'], title='Network')
    network_table.sortby = 'network'
    network_table.align = 'l'
    speeds = []
    ded_host_speeds = []
    for option in create_options['networkComponents']:
        template = option.get('template', None)
        price = option.get('itemPrice', None)

        if not template or not price \
                or not template.get('networkComponents', None):
            continue

        if not template['networkComponents'][0] \
                or not template['networkComponents'][0].get('maxSpeed', None):
            continue

        max_speed = str(template['networkComponents'][0]['maxSpeed'])
        if price.get('dedicatedHostInstanceFlag', False) \
                and max_speed not in ded_host_speeds:
            ded_host_speeds.append(max_speed)
        elif max_speed not in speeds:
            speeds.append(max_speed)

    speeds = sorted(speeds)
    network_table.add_row(['nic', formatting.listing(speeds, separator=',')])

    ded_host_speeds = sorted(ded_host_speeds)
    network_table.add_row(['nic (dedicated host)',
                           formatting.listing(ded_host_speeds, separator=',')])
    return network_table
