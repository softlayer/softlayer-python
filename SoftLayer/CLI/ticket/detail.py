"""Get details for a ticket."""
# :license: MIT, see LICENSE for more details.

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import helpers
from SoftLayer.CLI import ticket

import click


@click.command()
@click.argument('identifier')
@click.option('--count', type=click.INT, help="Number of updates", default=10)
@environment.pass_env
def cli(env, identifier, count):
    """Get details for a ticket."""

    mgr = SoftLayer.TicketManager(env.client)

    ticket_id = helpers.resolve_id(mgr.resolve_ids, identifier, 'ticket')
    return ticket.get_ticket_results(mgr, ticket_id, update_count=count)
