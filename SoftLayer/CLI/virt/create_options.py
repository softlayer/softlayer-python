"""Virtual server order options."""
# :license: MIT, see LICENSE for more details.
import os
import os.path

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting


@click.command()
@environment.pass_env
def cli(env):
    """Virtual server order options."""

    vsi = SoftLayer.VSManager(env.client)
    result = vsi.get_create_options()

    table = formatting.KeyValueTable(['name', 'value'])
    table.align['name'] = 'r'
    table.align['value'] = 'l'

    # Datacenters
    datacenters = [dc['template']['datacenter']['name']
                   for dc in result['datacenters']]
    datacenters = sorted(datacenters)

    table.add_row(['datacenter',
                   formatting.listing(datacenters, separator='\n')])

    bal_flavors = [x for x in result['flavors']
                   if x['flavor']['keyName'].startswith('B1')]
    bal_loc_hdd_flavors = [x for x in result['flavors']
                           if x['flavor']['keyName'].startswith('BL1')]
    bal_loc_ssd_flavors = [x for x in result['flavors']
                           if x['flavor']['keyName'].startswith('BL2')]
    compute_flavors = [x for x in result['flavors']
                       if x['flavor']['keyName'].startswith('C1')]
    memory_flavors = [x for x in result['flavors']
                      if x['flavor']['keyName'].startswith('M1')]

    def add_flavors_row(flavor_options, name):
        """Add Flavor rows to the table."""

        flavors = []
        for flavor_option in flavor_options:
            flavors.append(str(flavor_option['flavor']['keyName']))

        table.add_row(['flavors (%s)' % name,
                       formatting.listing(flavors, separator='\n')])

    add_flavors_row(bal_flavors, 'balanced')
    add_flavors_row(bal_loc_hdd_flavors, 'balanced local - hdd')
    add_flavors_row(bal_loc_ssd_flavors, 'balanced local - ssd')
    add_flavors_row(compute_flavors, 'compute')
    add_flavors_row(memory_flavors, 'memory')

    # CPUs
    standard_cpus = [x for x in result['processors']
                     if not x['template'].get('dedicatedAccountHostOnlyFlag',
                                              False)
                     and not x['template'].get('dedicatedHost', None)]
    ded_cpus = [x for x in result['processors']
                if x['template'].get('dedicatedAccountHostOnlyFlag', False)]
    ded_host_cpus = [x for x in result['processors']
                     if x['template'].get('dedicatedHost', None)]

    def add_cpus_row(cpu_options, name):
        """Add CPU rows to the table."""

        cpus = []
        for cpu_option in cpu_options:
            cpus.append(int(cpu_option['template']['startCpus']))

        table.add_row(['cpus (%s)' % name,
                       formatting.listing(cpus, separator=',')])

    standard_cpus = sorted(standard_cpus)
    add_cpus_row(standard_cpus, 'standard')

    ded_cpus = sorted(ded_cpus)
    add_cpus_row(ded_cpus, 'dedicated')

    ded_host_cpus = sorted(ded_host_cpus)
    add_cpus_row(ded_host_cpus, 'dedicated host')

    # Memory
    memory = [int(m['template']['maxMemory']) for m in result['memory']
              if not m['itemPrice'].get('dedicatedHostInstanceFlag', False)]
    ded_host_memory = [int(m['template']['maxMemory']) for m in result['memory']
                       if m['itemPrice'].get('dedicatedHostInstanceFlag', False)]

    memory = sorted(memory)
    table.add_row(['memory',
                   formatting.listing(memory, separator=',')])

    ded_host_memory = sorted(ded_host_memory)
    table.add_row(['memory (dedicated host)',
                   formatting.listing(ded_host_memory, separator=',')])

    # Operating Systems
    op_sys = [o['template']['operatingSystemReferenceCode'] for o in
              result['operatingSystems']]

    op_sys = sorted(op_sys)
    os_summary = set()

    for operating_system in op_sys:
        os_summary.add(operating_system[0:operating_system.find('_')])

    for summary in sorted(os_summary):
        table.add_row([
            'os (%s)' % summary,
            os.linesep.join(sorted([x for x in op_sys
                                    if x[0:len(summary)] == summary]))
        ])

    # Disk
    local_disks = [x for x in result['blockDevices']
                   if x['template'].get('localDiskFlag', False)
                   and not x['itemPrice'].get('dedicatedHostInstanceFlag',
                                              False)]

    ded_host_local_disks = [x for x in result['blockDevices']
                            if x['template'].get('localDiskFlag', False)
                            and x['itemPrice'].get('dedicatedHostInstanceFlag',
                                                   False)]

    san_disks = [x for x in result['blockDevices']
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
            table.add_row(['%s disk(%s)' % (name, label),
                           formatting.listing(simple[label],
                                              separator=',')])

    add_block_rows(san_disks, 'san')
    add_block_rows(local_disks, 'local')
    add_block_rows(ded_host_local_disks, 'local (dedicated host)')

    # Network
    speeds = []
    ded_host_speeds = []
    for option in result['networkComponents']:
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
    table.add_row(['nic', formatting.listing(speeds, separator=',')])

    ded_host_speeds = sorted(ded_host_speeds)
    table.add_row(['nic (dedicated host)',
                   formatting.listing(ded_host_speeds, separator=',')])

    env.fout(table)
