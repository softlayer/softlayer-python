"""Update firmware."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.argument('identifier')
@click.option('-i', '--ipmi', is_flag=True, help="Update IPMI firmware")
@click.option('-r', '--raid', is_flag=True, help="Update RAID firmware")
@click.option('-b', '--bios', is_flag=True, help="Update BIOS firmware")
@click.option('-d', '--harddrive', is_flag=True, help="Update Hard Drives firmware")
@click.option('-n', '--network', is_flag=True, help="Update Network Card firmware")
@environment.pass_env
def cli(env, identifier, ipmi, raid, bios, harddrive, network):
    """Update server firmware. By default will update all available server components."""

    mgr = SoftLayer.HardwareManager(env.client)
    hw_id = helpers.resolve_id(mgr.resolve_ids, identifier, 'hardware')
    confirm_message = f"This will power off the server with id {hw_id} and update device firmware. Continue?"
    if not (env.skip_confirmations or formatting.confirm(confirm_message)):
        raise exceptions.CLIAbort('Aborted.')

    # If no options were specified, set them all to enabled.
    if not any([ipmi, raid, bios, harddrive, network]):
        ipmi = raid = bios = harddrive = network = 1
    mgr.update_firmware(hw_id, ipmi, raid, bios, harddrive, network)
    env.fout(f"[green]Firmware update for {identifier} started")
