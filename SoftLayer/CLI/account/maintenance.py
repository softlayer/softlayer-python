"""Account Maintance manager"""
# :license: MIT, see LICENSE for more details.
from pprint import pprint as pp
import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer.managers.account import AccountManager as AccountManager
from SoftLayer import utils

@click.command()

@environment.pass_env
def cli(env):
    """Summary and acknowledgement of upcoming and ongoing maintenance"""

    # Print a list of all on going maintenance 
    manager = AccountManager(env.client)
    events = manager.get_upcoming_events()
    env.fout(event_table(events))
    # pp(events)

    # Allow ack all, or ack specific maintenance

def event_table(events):
    table = formatting.Table([
        "Id",
        "Start Date",
        "End Date",
        "Subject",
        "Status",
        "Acknowledged",
        "Updates",
        "Impacted Resources"
    ], title="Upcoming Events")
    table.align['Subject'] = 'l'
    table.align['Impacted Resources'] = 'l'
    for event in events:
        table.add_row([
            event.get('id'),
            utils.clean_time(event.get('startDate')),
            utils.clean_time(event.get('endDate')),
            event.get('subject'),
            utils.lookup(event, 'statusCode', 'name'),
            event.get('acknowledgedFlag'),
            event.get('updateCount'),
            event.get('impactedResourceCount')
        ])
    return table