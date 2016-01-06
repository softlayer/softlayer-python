"""Adds an update to an existing ticket."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import helpers
from SoftLayer.CLI import ticket


@click.command()
@click.argument('identifier')
@click.option('--body', help="The entry that will be appended to the ticket")
@environment.pass_env
def cli(env, identifier, body):
    """Adds an update to an existing ticket."""
    mgr = SoftLayer.TicketManager(env.client)

    ticket_id = helpers.resolve_id(mgr.resolve_ids, identifier, 'ticket')

    if body is None:
        body = click.edit('\n\n' + ticket.TEMPLATE_MSG)

    mgr.update_ticket(ticket_id=ticket_id, body=body)
    env.fout("Ticket Updated!")
