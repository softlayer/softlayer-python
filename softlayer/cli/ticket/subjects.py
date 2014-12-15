"""List Subject IDs for ticket creation."""
# :license: MIT, see LICENSE for more details.

import softlayer
from softlayer.cli import environment
from softlayer.cli import formatting


import click


@click.command()
@environment.pass_env
def cli(env):
    """List Subject IDs for ticket creation."""
    ticket_mgr = softlayer.TicketManager(env.client)

    table = formatting.Table(['id', 'subject'])
    for subject in ticket_mgr.list_subjects():
        table.add_row([subject['id'], subject['name']])

    return table
