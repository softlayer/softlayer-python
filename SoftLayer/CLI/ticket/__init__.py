"""Support tickets."""

from SoftLayer.CLI import formatting
from SoftLayer import utils

import click


TEMPLATE_MSG = "***** SoftLayer Ticket Content ******"


def get_ticket_results(mgr, ticket_id, update_count=1):
    """Get output about a ticket.

    :param integer id: the ticket ID
    :param integer update_count: number of entries to retrieve from ticket
    :returns: a KeyValue table containing the details of the ticket

    """
    result = mgr.get_ticket(ticket_id)
    result = utils.NestedDict(result)

    table = formatting.KeyValueTable(['Name', 'Value'])
    table.align['Name'] = 'r'
    table.align['Value'] = 'l'

    table.add_row(['id', result['id']])
    table.add_row(['title', result['title']])
    if result['assignedUser']:
        table.add_row(['assignedUser',
                       "%s %s" % (result['assignedUser']['firstName'],
                                  result['assignedUser']['lastName'])])
    table.add_row(['createDate', result['createDate']])
    table.add_row(['lastEditDate', result['lastEditDate']])

    total_update_count = result['updateCount']
    count = min(total_update_count, update_count)
    for i, update in enumerate(result['updates'][:count]):
        # NOTE(kmcdonald): Windows new-line characters need to be stripped out
        wrapped_entry = click.wrap_text(update['entry'].replace('\r', ''))
        table.add_row(['Update %s' % (i + 1,), wrapped_entry])

    return table
