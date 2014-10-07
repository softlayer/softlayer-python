"""List tickets."""
# :license: MIT, see LICENSE for more details.

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting


import click


@click.command()
@click.option('--open / --closed', 'is_open', help="Display closed tickets")
@environment.pass_env
def cli(env, is_open):
    """List tickets."""
    ticket_mgr = SoftLayer.TicketManager(env.client)

    tickets = ticket_mgr.list_tickets(open_status=not is_open,
                                      closed_status=is_open)

    table = formatting.Table(['id', 'assigned user', 'title',
                              'creation date', 'last edit date'])

    for ticket in tickets:
        user = 'N/A'
        if ticket.get('assignedUser'):
            user = "%s %s" % (ticket['assignedUser']['firstName'],
                              ticket['assignedUser']['lastName']),

        table.add_row([
            ticket['id'],
            user,
            click.wrap_text(ticket['title']),
            ticket['createDate'],
            ticket['lastEditDate']
        ])

    return table
