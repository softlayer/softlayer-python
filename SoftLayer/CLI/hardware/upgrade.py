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
@click.option('--test', is_flag=True, default=False, help="Do not actually upgrade the hardware server")
@environment.pass_env
def cli(env, identifier, memory, network, drive_controller, public_bandwidth, test):
    """Upgrade a Hardware Server."""

    mgr = SoftLayer.HardwareManager(env.client)

    if not any([memory, network, drive_controller, public_bandwidth]):
        raise exceptions.ArgumentError("Must provide "
                                       " [--memory], [--network], [--drive-controller], or [--public-bandwidth]")

    hw_id = helpers.resolve_id(mgr.resolve_ids, identifier, 'Hardware')
    if not test:
        if not (env.skip_confirmations or formatting.confirm(
                "This action will incur charges on your account. Continue?")):
            raise exceptions.CLIAbort('Aborted')

    if not mgr.upgrade(hw_id, memory=memory, nic_speed=network, drive_controller=drive_controller,
                       public_bandwidth=public_bandwidth, test=test):
        raise exceptions.CLIAbort('Hardware Server Upgrade Failed')
    env.fout('Successfully Upgraded.')
