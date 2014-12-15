"""Get details for a ticket."""
# :license: MIT, see LICENSE for more details.

import softlayer
from softlayer.cli import environment
from softlayer.cli import helpers
from softlayer.cli import ticket

import click


@click.command()
@click.argument('identifier')
@click.option('--count', type=click.INT, help="Number of updates", default=10)
@environment.pass_env
def cli(env, identifier, count):
    """Get details for a ticket."""

    mgr = softlayer.TicketManager(env.client)

    ticket_id = helpers.resolve_id(mgr.resolve_ids, identifier, 'ticket')
    return ticket.get_ticket_results(mgr, ticket_id, update_count=count)
