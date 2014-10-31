"""List Subject IDs for ticket creation."""
# :license: MIT, see LICENSE for more details.

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting


import click


@click.command()
@environment.pass_env
def cli(env):
    """List Subject IDs for ticket creation."""
    ticket_mgr = SoftLayer.TicketManager(env.client)

    table = formatting.Table(['id', 'subject'])
    for subject in ticket_mgr.list_subjects():
        table.add_row([subject['id'], subject['name']])

    return table
