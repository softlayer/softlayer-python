"""List tickets."""
# :license: MIT, see LICENSE for more details.

import click
from SoftLayer import utils

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.option('--open / --closed', 'is_open', default=True,
              help="Display only open or closed tickets")
@click.option('--limit', default=100, show_default=True, type=click.INT, help="Result limit")
@click.option("--all", "-a", "all_tickets", is_flag=True, default=False, help="Return all tickets")
@environment.pass_env
def cli(env, is_open, limit, all_tickets):
    """List tickets."""
    ticket_mgr = SoftLayer.TicketManager(env.client)
    table = formatting.Table([
        'id', 'Case_Number', 'assigned_user', 'title', 'last_edited', 'status', 'updates', 'priority'
    ])

    tickets = ticket_mgr.list_tickets(open_status=is_open,
                                      closed_status=not is_open, limit=limit, all_tickets=all_tickets)

    for ticket in tickets:
        user = formatting.blank()
        if ticket.get('assignedUser'):
            user = "%s %s" % (ticket['assignedUser']['firstName'], ticket['assignedUser']['lastName'])

        table.add_row([
            ticket['id'],
            ticket['serviceProviderResourceId'],
            user,
            click.wrap_text(ticket['title']),
            utils.clean_time(ticket.get('lastEditDate'), out_format="%Y-%m-%d"),
            ticket['status']['name'],
            ticket.get('updateCount', 0),
            ticket.get('priority', 0)
        ])

    env.fout(table)
