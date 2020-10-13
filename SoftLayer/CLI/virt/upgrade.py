"""Upgrade a virtual server."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers
from SoftLayer.CLI import virt


@click.command(epilog="""Note: SoftLayer automatically reboots the VS once
upgrade request is placed. The VS is halted until the Upgrade transaction is
completed. However for Network, no reboot is required.""")
@click.argument('identifier')
@click.option('--cpu', type=click.INT, help="Number of CPU cores")
@click.option('--private', is_flag=True,
              help="CPU core will be on a dedicated host server.")
@click.option('--memory', type=virt.MEM_TYPE, help="Memory in megabytes")
@click.option('--network', type=click.INT, help="Network port speed in Mbps")
@click.option('--add-disk', type=click.INT, multiple=True, required=False, help="add Hard disk in GB")
@click.option('--resize-disk', nargs=2, multiple=True, type=(int, int),
              help="Update disk number to size in GB. --resize-disk 250 2 ")
@click.option('--flavor', type=click.STRING,
              help="Flavor keyName\nDo not use --memory, --cpu or --private, if you are using flavors")
@environment.pass_env
def cli(env, identifier, cpu, private, memory, network, flavor, add_disk, resize_disk):
    """Upgrade a virtual server."""

    vsi = SoftLayer.VSManager(env.client)

    if not any([cpu, memory, network, flavor, resize_disk, add_disk]):
        raise exceptions.ArgumentError("Must provide [--cpu],"
                                       " [--memory], [--network], [--flavor], [--resize-disk], or [--add] to upgrade")

    if private and not cpu:
        raise exceptions.ArgumentError("Must specify [--cpu] when using [--private]")

    vs_id = helpers.resolve_id(vsi.resolve_ids, identifier, 'VS')
    if not (env.skip_confirmations or formatting.confirm("This action will incur charges on your account. Continue?")):
        raise exceptions.CLIAbort('Aborted')

    disk_json = list()
    if memory:
        memory = int(memory / 1024)
    if resize_disk:
        for guest_disk in resize_disk:
            disks = {'capacity': guest_disk[0], 'number': guest_disk[1]}
            disk_json.append(disks)

    elif add_disk:
        for guest_disk in add_disk:
            disks = {'capacity': guest_disk, 'number': -1}
            disk_json.append(disks)

    if not vsi.upgrade(vs_id, cpus=cpu, memory=memory, nic_speed=network, public=not private, preset=flavor,
                       disk=disk_json):
        raise exceptions.CLIAbort('VS Upgrade Failed')
