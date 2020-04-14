"""Get details for a ticket."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import helpers
from SoftLayer.CLI import ticket


@click.command()
@click.argument('identifier')
@click.option('--count',
              type=click.INT,
              help="Number of updates",
              show_default=True,
              default=10)
@environment.pass_env
def cli(env, identifier, count):
    """Get details for a ticket."""

    is_json = False
    if env.format == 'json':
        is_json = True
    mgr = SoftLayer.TicketManager(env.client)

    ticket_id = helpers.resolve_id(mgr.resolve_ids, identifier, 'ticket')
    env.fout(ticket.get_ticket_results(mgr, ticket_id, is_json, update_count=count))
