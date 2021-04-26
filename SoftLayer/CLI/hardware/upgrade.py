"""Upgrade a hardware server."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers


@click.command()
@click.argument('identifier')
@click.option('--memory', type=click.INT, help="Memory Size in GB")
@click.option('--network', help="Network port speed in Mbps",
              default=None,
              type=click.Choice(['100', '100 Redundant', '100 Dual',
                                 '1000', '1000 Redundant', '1000 Dual',
                                 '10000', '10000 Redundant', '10000 Dual'])
              )
@click.option('--drive-controller',
              help="Drive Controller",
              default=None,
              type=click.Choice(['Non-RAID', 'RAID']))
@click.option('--public-bandwidth', type=click.INT, help="Public Bandwidth in GB")
@click.option('--add-disk', nargs=2, multiple=True, type=(int, int),
              help="Add a Hard disk in GB to a specific channel, e.g 1000 GB in disk2, it will be "
                   "--add-disk 1000 2")
@click.option('--resize-disk', nargs=2, multiple=True, type=(int, int),
              help="Upgrade a specific disk size in GB, e.g --resize-disk 2000 2")
@click.option('--test', is_flag=True, default=False, help="Do not actually upgrade the hardware server")
@environment.pass_env
def cli(env, identifier, memory, network, drive_controller, public_bandwidth, add_disk, resize_disk, test):
    """Upgrade a Hardware Server."""

    mgr = SoftLayer.HardwareManager(env.client)

    if not any([memory, network, drive_controller, public_bandwidth, add_disk, resize_disk]):
        raise exceptions.ArgumentError("Must provide "
                                       " [--memory], [--network], [--drive-controller], [--public-bandwidth],"
                                       "[--add-disk] or [--resize-disk]")

    hw_id = helpers.resolve_id(mgr.resolve_ids, identifier, 'Hardware')
    if not test:
        if not (env.skip_confirmations or formatting.confirm(
                "This action will incur charges on your account. Continue?")):
            raise exceptions.CLIAbort('Aborted')

    disk_list = list()
    if add_disk:
        for guest_disk in add_disk:
            disks = {'description': 'add_disk', 'capacity': guest_disk[0], 'number': guest_disk[1]}
            disk_list.append(disks)
    if resize_disk:
        for guest_disk in resize_disk:
            disks = {'description': 'resize_disk', 'capacity': guest_disk[0], 'number': guest_disk[1]}
            disk_list.append(disks)

    if not mgr.upgrade(hw_id, memory=memory, nic_speed=network, drive_controller=drive_controller,
                       public_bandwidth=public_bandwidth, disk=disk_list, test=test):
        raise exceptions.CLIAbort('Hardware Server Upgrade Failed')
    env.fout('Successfully Upgraded.')
