"""List tickets."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting


@click.command()
@click.option('--open / --closed', 'is_open', default=True,
              help="Display only open or closed tickets")
@environment.pass_env
def cli(env, is_open):
    """List tickets."""
    ticket_mgr = SoftLayer.TicketManager(env.client)
    table = formatting.Table([
        'id', 'assigned_user', 'title', 'last_edited', 'status', 'updates', 'priority'
    ])

    tickets = ticket_mgr.list_tickets(open_status=is_open, closed_status=not is_open)
    for ticket in tickets:
        user = formatting.blank()
        if ticket.get('assignedUser'):
            user = "%s %s" % (ticket['assignedUser']['firstName'], ticket['assignedUser']['lastName'])

        table.add_row([
            ticket['id'],
            user,
            click.wrap_text(ticket['title']),
            ticket['lastEditDate'],
            ticket['status']['name'],
            ticket.get('updateCount', 0),
            ticket.get('priority', 0)
        ])

    env.fout(table)
