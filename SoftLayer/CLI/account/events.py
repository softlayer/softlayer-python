"""Summary and acknowledgement of upcoming and ongoing maintenance events"""
# :license: MIT, see LICENSE for more details.
import click

from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.managers.account import AccountManager as AccountManager
from SoftLayer import utils


@click.command()
@click.option('--ack-all', is_flag=True, default=False,
              help="Acknowledge every upcoming event. Doing so will turn off the popup in the control portal")
@environment.pass_env
def cli(env, ack_all):
    """Summary and acknowledgement of upcoming and ongoing maintenance events"""

    manager = AccountManager(env.client)
    events = manager.get_upcoming_events()

    if ack_all:
        for event in events:
            result = manager.ack_event(event['id'])
            event['acknowledgedFlag'] = result
    env.fout(event_table(events))


def event_table(events):
    """Formats a table for events"""
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
            # Some subjects can have \r\n for some reason.
            utils.clean_splitlines(event.get('subject')),
            utils.lookup(event, 'statusCode', 'name'),
            event.get('acknowledgedFlag'),
            event.get('updateCount'),
            event.get('impactedResourceCount')
        ])
    return table
