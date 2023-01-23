"""List dedicated hosts."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI.command import SLCommand as SLCommand
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer import utils


@click.command(cls=SLCommand, short_help="List virtual servers.")
@click.option('--name', '-n', help='Filter by name of the dedicated host')
@click.option('--datacenter', '-d', help='Filter by datacenter of the dedicated host')
@click.option('--owner', help='Filter by owner of the dedicated host')
@click.option('--order', help='Filter by ID of the order which purchased this dedicated host', type=click.INT)
@environment.pass_env
def cli(env, name, datacenter, owner, order,):
    """List dedicated hosts."""

    object_mask = "mask[id,name,createDate,cpuCount,diskCapacity,memoryCapacity,guestCount," \
                  "datacenter,backendRouter,allocationStatus,billingItem[orderItem[order[userRecord]]]]"
    object_filter = {}

    if datacenter is not None:
        object_filter = {
            "dedicatedHosts": {
                "datacenter": {
                    "name": {
                        "operation": datacenter
                    }
                }
            }
        }

    if name is not None:
        object_name_filter = {
            "dedicatedHosts": {
                "name": {
                    "operation": name
                }
            }
        }
        object_filter = utils.dict_merge(object_filter, object_name_filter)

    if owner is not None:
        object_owner_filter = {
            "dedicatedHosts": {
                "billingItem": {
                    "orderItem": {
                        "order": {
                            "userRecord": {
                                "username": {
                                    "operation": owner
                                }
                            }
                        }
                    }
                }
            }
        }
        object_filter = utils.dict_merge(object_filter, object_owner_filter)

    if order is not None:
        object_order_filter = {
            "dedicatedHosts": {
                "billingItem": {
                    "orderItem": {
                        "order": {
                            "id": {
                                "operation": order
                            }
                        }
                    }
                }
            }
        }
        object_filter = utils.dict_merge(object_filter, object_order_filter)

    vsi = SoftLayer.AccountManager(env.client)
    dedicated_hosts = vsi.get_dedicated_hosts(object_mask, object_filter)
    table = formatting.Table(["Id", "Name", "Datacenter", "Router", "CPU (allocated/total)",
                              "Memory (allocated/total)", "Disk (allocated/total)", "Guests"])
    table.align['Name'] = 'l'

    if len(dedicated_hosts) == 0:
        click.secho("No dedicated hosts are found.")
    else:
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
