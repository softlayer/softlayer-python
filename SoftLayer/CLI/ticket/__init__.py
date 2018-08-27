"""Support tickets."""

import click

from SoftLayer.CLI import formatting


TEMPLATE_MSG = "***** SoftLayer Ticket Content ******"

# https://softlayer.github.io/reference/services/SoftLayer_Ticket_Priority/getPriorities/
PRIORITY_MAP = [
    'No Priority',
    'Severity 1 - Critical Impact / Service Down',
    'Severity 2 - Significant Business Impact',
    'Severity 3 - Minor Business Impact',
    'Severity 4 - Minimal Business Impact'
]


def get_ticket_results(mgr, ticket_id, update_count=1):
    """Get output about a ticket.

    :param integer id: the ticket ID
    :param integer update_count: number of entries to retrieve from ticket
    :returns: a KeyValue table containing the details of the ticket

    """
    ticket = mgr.get_ticket(ticket_id)

    table = formatting.KeyValueTable(['name', 'value'])
    table.align['name'] = 'r'
    table.align['value'] = 'l'

    table.add_row(['id', ticket['id']])
    table.add_row(['title', ticket['title']])
    table.add_row(['priority', PRIORITY_MAP[ticket.get('priority', 0)]])
    if ticket.get('assignedUser'):
        user = ticket['assignedUser']
        table.add_row([
            'user',
            "%s %s" % (user.get('firstName'), user.get('lastName')),
        ])

    table.add_row(['status', ticket['status']['name']])
    table.add_row(['created', ticket.get('createDate')])
    table.add_row(['edited', ticket.get('lastEditDate')])

    # Only show up to the specified update count
    updates = ticket.get('updates', [])
    count = min(len(updates), update_count)
    count_offset = len(updates) - count + 1  # Display as one-indexed
    for i, update in enumerate(updates[-count:]):
        wrapped_entry = ""

        # Add user details (fields are different between employee and users)
        editor = update.get('editor')
        if editor:
            if editor.get('displayName'):
                wrapped_entry += "By %s (Employee)\n" % (editor['displayName'])
            if editor.get('firstName'):
                wrapped_entry += "By %s %s\n" % (editor.get('firstName'),
                                                 editor.get('lastName'))

        # NOTE(kmcdonald): Windows new-line characters need to be stripped out
        wrapped_entry += click.wrap_text(update['entry'].replace('\r', ''))
        table.add_row(['update %s' % (count_offset + i,), wrapped_entry])

    return table
