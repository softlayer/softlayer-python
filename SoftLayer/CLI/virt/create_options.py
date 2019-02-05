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

    def _add_flavor_rows(flavor_key, flavor_label, flavor_options):
        flavors = []

        for flavor_option in flavor_options:
            flavor_key_name = utils.lookup(flavor_option, 'flavor', 'keyName')
            if not flavor_key_name.startswith(flavor_key):
                continue

            flavors.append(flavor_key_name)

        if len(flavors) > 0:
            table.add_row(['flavors (%s)' % flavor_label,
                           formatting.listing(flavors, separator='\n')])

    if result.get('flavors', None):
        _add_flavor_rows('B1', 'balanced', result['flavors'])
        _add_flavor_rows('BL1', 'balanced local - hdd', result['flavors'])
        _add_flavor_rows('BL2', 'balanced local - ssd', result['flavors'])
        _add_flavor_rows('C1', 'compute', result['flavors'])
        _add_flavor_rows('M1', 'memory', result['flavors'])
        _add_flavor_rows('AC', 'GPU', result['flavors'])

    # CPUs
    standard_cpus = [int(x['template']['startCpus']) for x in result['processors']
                     if not x['template'].get('dedicatedAccountHostOnlyFlag',
                                              False)
                     and not x['template'].get('dedicatedHost', None)]
    ded_cpus = [int(x['template']['startCpus']) for x in result['processors']
                if x['template'].get('dedicatedAccountHostOnlyFlag', False)]
    ded_host_cpus = [int(x['template']['startCpus']) for x in result['processors']
                     if x['template'].get('dedicatedHost', None)]

    standard_cpus = sorted(standard_cpus)
    table.add_row(['cpus (standard)', formatting.listing(standard_cpus, separator=',')])
    ded_cpus = sorted(ded_cpus)
    table.add_row(['cpus (dedicated)', formatting.listing(ded_cpus, separator=',')])
    ded_host_cpus = sorted(ded_host_cpus)
    table.add_row(['cpus (dedicated host)', formatting.listing(ded_host_cpus, separator=',')])

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
