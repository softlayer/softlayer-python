"""Adds an update to an existing ticket."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import helpers
from SoftLayer.CLI import ticket


@click.command()
@click.argument('identifier')
@click.option('--body', help="Text to add to the ticket. STDIN or the default text editor will be used otherwise.")
@environment.pass_env
def cli(env, identifier, body):
    """Adds an update to an existing ticket.

Will update the ticket with `Some text`.::

        slcli ticket update 123456 --body="Some text"

Will update the ticket with text from STDIN::

        cat sometfile.txt | slcli ticket update 123456

Will open the default text editor, and once closed, use that text to update the ticket::

        slcli ticket update 123456
    """
    mgr = SoftLayer.TicketManager(env.client)

    ticket_id = helpers.resolve_id(mgr.resolve_ids, identifier, 'ticket')
    if body is None:
        stdin = click.get_text_stream('stdin')
        # Means there is text on the STDIN buffer, read it and add to the ticket
        if not stdin.isatty():
            body = stdin.read()
        # This is an interactive terminal, open a text editor
        else:
            body = click.edit('\n\n' + ticket.TEMPLATE_MSG)
    mgr.update_ticket(ticket_id=ticket_id, body=body)
    env.fout("Ticket Updated!")
