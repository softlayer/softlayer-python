"""List dedicated servers."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@helpers.multi_option('--tag', help='Filter by tags')
@click.option('--sortby', help='Column to sort by',
              default='Name',
              show_default=True)
@click.option('--datacenter', '-d', help='Filter by datacenter shortname')
@click.option('--name', '-H', help='Filter by host portion of the FQDN')
@click.option('--order', help='Filter by ID of the order which purchased this dedicated host', type=click.INT)
@click.option('--owner', help='Filter by owner of the dedicated host')
@environment.pass_env
def cli(env, sortby, datacenter, name, tag, order, owner):
    """List dedicated host."""
    mgr = SoftLayer.DedicatedHostManager(env.client)
    dedicated_hosts = mgr.list_instances(datacenter=datacenter,
                                         hostname=name,
                                         tags=tag,
                                         order=order,
                                         owner=owner)

    table = formatting.Table(["Id", "Name", "Datacenter", "Router", "CPU (allocated/total)",
                              "Memory (allocated/total)", "Disk (allocated/total)", "Guests"])
    table.align['Name'] = 'l'
    table.sortby = sortby

    if len(dedicated_hosts) != 0:
        for host in dedicated_hosts:
            cpu_allocated = host.get('allocationStatus').get('cpuAllocated')
            cpu_total = host.get('allocationStatus').get('cpuCount')
            memory_allocated = host.get('allocationStatus').get('memoryAllocated')
            memory_total = host.get('allocationStatus').get('memoryCapacity')
            disk_allocated = host.get('allocationStatus').get('diskAllocated')
            disk_total = host.get('allocationStatus').get('diskCapacity')
            table.add_row([
                host.get('id'),
                host.get('name'),
                host.get('datacenter').get('name'),
                host.get('backendRouter').get('hostname'),
                f"{cpu_allocated}/{cpu_total}",
                f"{memory_allocated}/{memory_total}",
                f"{disk_allocated}/{disk_total}",
                host.get('guestCount')
            ])

        env.fout(table)
    else:
        click.secho("No dedicated hosts are found.")
