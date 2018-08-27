"""Create a support ticket."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import helpers
from SoftLayer.CLI import ticket


@click.command()
@click.option('--title', required=True, help="The title of the ticket")
@click.option('--subject-id', type=int, required=True,
              help="""The subject id to use for the ticket,
 issue 'slcli ticket subjects' to get the list""")
@click.option('--body', help="The ticket body")
@click.option('--hardware', 'hardware_identifier',
              help="The identifier for hardware to attach")
@click.option('--virtual', 'virtual_identifier',
              help="The identifier for a virtual server to attach")
@click.option('--priority', 'priority', type=click.Choice(['1', '2', '3', '4']), default=None,
              help="""Ticket priority, from 1 (Critical) to 4 (Minimal Impact).
              Only settable with Advanced and Premium support. See https://www.ibm.com/cloud/support""")
@environment.pass_env
def cli(env, title, subject_id, body, hardware_identifier, virtual_identifier, priority):
    """Create a support ticket."""
    ticket_mgr = SoftLayer.TicketManager(env.client)

    if body is None:
        body = click.edit('\n\n' + ticket.TEMPLATE_MSG)
    created_ticket = ticket_mgr.create_ticket(
        title=title,
        body=body,
        subject=subject_id,
        priority=priority)

    if hardware_identifier:
        hardware_mgr = SoftLayer.HardwareManager(env.client)
        hardware_id = helpers.resolve_id(hardware_mgr.resolve_ids, hardware_identifier, 'hardware')
        ticket_mgr.attach_hardware(created_ticket['id'], hardware_id)

    if virtual_identifier:
        vs_mgr = SoftLayer.VSManager(env.client)
        vs_id = helpers.resolve_id(vs_mgr.resolve_ids, virtual_identifier, 'VS')
        ticket_mgr.attach_virtual_server(created_ticket['id'], vs_id)

    env.fout(ticket.get_ticket_results(ticket_mgr, created_ticket['id']))
