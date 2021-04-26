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
              help="""The subject id to use for the ticket, run 'slcli ticket subjects' to get the list""")
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
    """Create a Infrastructure support ticket.

    Will create the ticket with `Some text`.::

        slcli ticket create --body="Some text" --subject-id 1522 --hardware 12345 --title "My New Ticket"

    Will create the ticket with text from STDIN::

        cat sometfile.txt | slcli ticket create --subject-id 1003 --virtual 111111 --title "Reboot Me"

    Will open the default text editor, and once closed, use that text to create the ticket::

        slcli ticket create --subject-id 1482 --title "Vyatta Questions..."

    """
    ticket_mgr = SoftLayer.TicketManager(env.client)
    if body is None:
        stdin = click.get_text_stream('stdin')
        # Means there is text on the STDIN buffer, read it and add to the ticket
        if not stdin.isatty():
            body = stdin.read()
        # This is an interactive terminal, open a text editor
        else:
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

    env.fout(ticket.get_ticket_results(ticket_mgr, False, created_ticket['id']))
