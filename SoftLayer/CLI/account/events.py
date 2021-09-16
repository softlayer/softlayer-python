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
    planned_events = manager.get_upcoming_events("PLANNED")
    unplanned_events = manager.get_upcoming_events("UNPLANNED_INCIDENT")
    announcement_events = manager.get_upcoming_events("ANNOUNCEMENT")

    add_ack_flag(planned_events, manager, ack_all)
    env.fout(planned_event_table(planned_events))

    add_ack_flag(unplanned_events, manager, ack_all)
    env.fout(unplanned_event_table(unplanned_events))

    add_ack_flag(announcement_events, manager, ack_all)
    env.fout(announcement_event_table(announcement_events))


def add_ack_flag(events, manager, ack_all):
    """Add acknowledgedFlag to the event"""
    if ack_all:
        for event in events:
            result = manager.ack_event(event['id'])
            event['acknowledgedFlag'] = result


def planned_event_table(events):
    """Formats a table for events"""
    planned_table = formatting.Table(['Event Data', 'Id', 'Event ID', 'Subject', 'Status', 'Items', 'Start Date',
                                      'End Date', 'Acknowledged', 'Updates'], title="Planned Events")
    planned_table.align['Subject'] = 'l'
    planned_table.align['Impacted Resources'] = 'l'
    for event in events:
        planned_table.add_row([
            utils.clean_time(event.get('startDate')),
            event.get('id'),
            event.get('systemTicketId'),
            # Some subjects can have \r\n for some reason.
            utils.clean_splitlines(event.get('subject')),
            utils.lookup(event, 'statusCode', 'name'),
            event.get('impactedResourceCount'),
            utils.clean_time(event.get('startDate')),
            utils.clean_time(event.get('endDate')),
            event.get('acknowledgedFlag'),
            event.get('updateCount'),

        ])
    return planned_table


def unplanned_event_table(events):
    """Formats a table for events"""
    unplanned_table = formatting.Table(['Id', 'Event ID', 'Subject', 'Status', 'Items', 'Start Date',
                                        'Last Updated', 'Acknowledged', 'Updates'], title="Unplanned Events")
    unplanned_table.align['Subject'] = 'l'
    unplanned_table.align['Impacted Resources'] = 'l'
    for event in events:
        unplanned_table.add_row([
            event.get('id'),
            event.get('systemTicketId'),
            # Some subjects can have \r\n for some reason.
            utils.clean_splitlines(event.get('subject')),
            utils.lookup(event, 'statusCode', 'name'),
            event.get('impactedResourceCount'),
            utils.clean_time(event.get('startDate')),
            utils.clean_time(event.get('modifyDate')),
            event.get('acknowledgedFlag'),
            event.get('updateCount'),
        ])
    return unplanned_table


def announcement_event_table(events):
    """Formats a table for events"""
    announcement_table = formatting.Table(
        ['Id', 'Event ID', 'Subject', 'Status', 'Items', 'Acknowledged', 'Updates'], title="Announcement Events")
    announcement_table.align['Subject'] = 'l'
    announcement_table.align['Impacted Resources'] = 'l'
    for event in events:
        announcement_table.add_row([
            event.get('id'),
            event.get('systemTicketId'),
            # Some subjects can have \r\n for some reason.
            utils.clean_splitlines(event.get('subject')),
            utils.lookup(event, 'statusCode', 'name'),
            event.get('impactedResourceCount'),
            event.get('acknowledgedFlag'),
            event.get('updateCount')
        ])
    return announcement_table
