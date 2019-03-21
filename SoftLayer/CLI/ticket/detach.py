"""Detach devices from a ticket."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import helpers


@click.command()
@click.argument('identifier', type=int)
@click.option('--hardware', 'hardware_identifier',
              help="The identifier for hardware to detach")
@click.option('--virtual', 'virtual_identifier',
              help="The identifier for a virtual server to detach")
@environment.pass_env
def cli(env, identifier, hardware_identifier, virtual_identifier):
    """Detach devices from a ticket."""
    ticket_mgr = SoftLayer.TicketManager(env.client)

    if hardware_identifier and virtual_identifier:
        raise exceptions.ArgumentError("Cannot detach hardware and a virtual server at the same time")

    if hardware_identifier:
        hardware_mgr = SoftLayer.HardwareManager(env.client)
        hardware_id = helpers.resolve_id(hardware_mgr.resolve_ids, hardware_identifier, 'hardware')
        ticket_mgr.detach_hardware(identifier, hardware_id)
    elif virtual_identifier:
        vs_mgr = SoftLayer.VSManager(env.client)
        vs_id = helpers.resolve_id(vs_mgr.resolve_ids, virtual_identifier, 'VS')
        ticket_mgr.detach_virtual_server(identifier, vs_id)
    else:
        raise exceptions.ArgumentError("Must have a hardware or virtual server identifier to detach")
