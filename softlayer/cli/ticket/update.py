"""Adds an update to an existing ticket."""
# :license: MIT, see LICENSE for more details.

import softlayer
from softlayer.cli import environment
from softlayer.cli import helpers
from softlayer.cli import ticket

import click


@click.command()
@click.argument('identifier')
@click.option('--body', help="The entry that will be appended to the ticket")
@environment.pass_env
def cli(env, identifier, body):
    """Adds an update to an existing ticket."""
    mgr = softlayer.TicketManager(env.client)

    ticket_id = helpers.resolve_id(mgr.resolve_ids, identifier, 'ticket')

    if body is None:
        body = click.edit('\n\n' + ticket.TEMPLATE_MSG)

    mgr.update_ticket(ticket_id=ticket_id, body=body)
    return "Ticket Updated!"
