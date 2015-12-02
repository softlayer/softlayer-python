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
    table.add_row(['datacenter',
                   formatting.listing(datacenters, separator='\n')])

    # CPUs
    standard_cpu = [x for x in result['processors']
                    if not x['template'].get(
                        'dedicatedAccountHostOnlyFlag', False)]

    ded_cpu = [x for x in result['processors']
               if x['template'].get('dedicatedAccountHostOnlyFlag',
                                    False)]

    def add_cpus_row(cpu_options, name):
        """Add CPU rows to the table."""
        cpus = []
        for cpu_option in cpu_options:
            cpus.append(str(cpu_option['template']['startCpus']))

        table.add_row(['cpus (%s)' % name,
                       formatting.listing(cpus, separator=',')])

    add_cpus_row(ded_cpu, 'private')
    add_cpus_row(standard_cpu, 'standard')

    # Memory
    memory = [str(m['template']['maxMemory']) for m in result['memory']]
    table.add_row(['memory',
                   formatting.listing(memory, separator=',')])

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
                   if x['template'].get('localDiskFlag', False)]

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

        for label in sorted(simple.keys()):
            table.add_row(['%s disk(%s)' % (name, label),
                           formatting.listing(simple[label],
                                              separator=',')])

    add_block_rows(local_disks, 'local')
    add_block_rows(san_disks, 'san')

    # Network
    speeds = []
    for comp in result['networkComponents']:
        speed = comp['template']['networkComponents'][0]['maxSpeed']
        speeds.append(str(speed))

    speeds = sorted(speeds)

    table.add_row(['nic', formatting.listing(speeds, separator=',')])

    env.fout(table)
