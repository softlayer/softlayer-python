"""
usage: sl ticket [<command>] [<args>...] [options]

Manages account tickets

The available commands are:
  create      Create a new ticket
  detail      Output details about an ticket
  list        List tickets
  update      Update an existing ticket
  subjects    List the subject IDs that can be used for ticket creation
  summary     Give summary info about tickets
"""
# :license: MIT, see LICENSE for more details.

import textwrap
import tempfile
import os
from subprocess import call

from SoftLayer import TicketManager
from SoftLayer.CLI import (CLIRunnable, Table, resolve_id, NestedDict,
                           KeyValueTable)

TEMPLATE_MSG = "***** SoftLayer Ticket Content ******"


def wrap_string(input_str):
    """ Utility method to wrap the a potentially long string to 80 chars """
    return textwrap.wrap(input_str, 80)


def get_ticket_results(mgr, ticket_id, update_count=1):
    """ Get output about a ticket

    :param integer id: the ticket ID
    :param integer update_count: number of entries to retrieve from ticket
    :returns: a KeyValue table containing the details of the ticket

    """
    result = mgr.get_ticket(ticket_id)
    result = NestedDict(result)

    table = KeyValueTable(['Name', 'Value'])
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
        update = wrap_string(update['entry'])
        table.add_row(['Update %s' % (i + 1,), update])

    return table


def open_editor(beg_msg, ending_msg=None):
    """

    :param beg_msg: generic msg to be appended at the end of the file
    :param ending_msg: placeholder msg to append at the end of the file,
            like filesystem info, etc, not being used now
    :returns: the content the user has entered

    """

    # Let's get the default EDITOR of the environment,
    # use nano if none is specified
    editor = os.environ.get('EDITOR', 'nano')

    with tempfile.NamedTemporaryFile(suffix=".tmp") as tfile:
        # populate the file with the baked messages
        tfile.write("\n")
        tfile.write(beg_msg)
        if ending_msg:
            tfile.write("\n")
            tfile.write(ending_msg)
        # flush the file and open it for editing
        tfile.flush()
        call([editor, tfile.name])
        tfile.seek(0)
        data = tfile.read()
        return data

    return


class ListTickets(CLIRunnable):
    """
usage: sl ticket list [options]

List tickets

Options:
  --closed  display closed tickets

"""
    action = 'list'

    def execute(self, args):
        ticket_mgr = TicketManager(self.client)

        tickets = ticket_mgr.list_tickets(
            open_status=not args.get('--closed'),
            closed_status=args.get('--closed'))

        table = Table(['id', 'assigned user', 'title',
                       'creation date', 'last edit date'])

        for ticket in tickets:
            if ticket['assignedUser']:
                table.add_row([
                    ticket['id'],
                    "%s %s" % (ticket['assignedUser']['firstName'],
                               ticket['assignedUser']['lastName']),
                    wrap_string(ticket['title']),
                    ticket['createDate'],
                    ticket['lastEditDate']
                ])
            else:
                table.add_row([
                    ticket['id'],
                    'N/A',
                    wrap_string(ticket['title']),
                    ticket['createDate'],
                    ticket['lastEditDate']
                ])

        return table


class ListSubjectsTickets(CLIRunnable):
    """
usage: sl ticket subjects [options]

List Subject IDs for ticket creation

"""
    action = 'subjects'

    def execute(self, args):
        ticket_mgr = TicketManager(self.client)

        table = Table(['id', 'subject'])
        for subject in ticket_mgr.list_subjects():
            table.add_row([
                subject['id'],
                subject['name']
            ])
        return table


class UpdateTicket(CLIRunnable):
    """
usage: sl ticket update <identifier> [options]

Updates a certain ticket

Options:
  --body=BODY  The entry that will be appended to the ticket

"""
    action = 'update'
    options = ['--body']

    def execute(self, args):
        mgr = TicketManager(self.client)

        ticket_id = resolve_id(
            mgr.resolve_ids, args.get('<identifier>'), 'ticket')

        body = args.get('--body')
        if body is None:
            body = open_editor(beg_msg=TEMPLATE_MSG)

        mgr.update_ticket(ticket_id=ticket_id, body=body)
        return "Ticket Updated!"


class TicketsSummary(CLIRunnable):
    """
usage: sl ticket summary [options]

Give summary info about tickets

"""
    action = 'summary'

    def execute(self, args):
        mask = ('mask[openTicketCount, closedTicketCount, '
                'openBillingTicketCount, openOtherTicketCount, '
                'openSalesTicketCount, openSupportTicketCount, '
                'openAccountingTicketCount]')
        account = self.client['Account'].getObject(mask=mask)
        table = Table(['Status', 'count'])

        nested = Table(['Type', 'count'])
        nested.add_row(['Accounting',
                        account['openAccountingTicketCount']])
        nested.add_row(['Billing', account['openBillingTicketCount']])
        nested.add_row(['Sales', account['openSalesTicketCount']])
        nested.add_row(['Support', account['openSupportTicketCount']])
        nested.add_row(['Other', account['openOtherTicketCount']])
        nested.add_row(['Total', account['openTicketCount']])
        table.add_row(['Open', nested])
        table.add_row(['Closed', account['closedTicketCount']])

        return table


class TicketDetails(CLIRunnable):
    """
usage: sl ticket detail  <identifier> [options]

Get details for a ticket

Options:
  --count=NUM  Show X count of updates [default: 10]
"""
    action = 'detail'

    def execute(self, args):
        mgr = TicketManager(self.client)

        ticket_id = resolve_id(
            mgr.resolve_ids, args.get('<identifier>'), 'ticket')

        count = args.get('--count')
        if count is None:
            count = 10
        return get_ticket_results(mgr, ticket_id, update_count=int(count))


class CreateTicket(CLIRunnable):
    """
usage: sl ticket create --title=TITLE --subject=ID [options]

Create a support ticket.

Required:
  --title=TITLE  The title of the ticket
  --subject=ID   The id of the subject to use for the ticket,
                 issue 'sl ticket subjects' to get the list

Optional:
  --body=BODY the body text to attach to the ticket,
              an editor will be opened if body is not provided
"""
    action = 'create'
    required_params = ['--title, --subject']

    def execute(self, args):
        mgr = TicketManager(self.client)
        if args.get('--title') is "":
            return 'Please provide a valid title'
        body = args.get('--body')
        if body is None:
            body = open_editor(beg_msg=TEMPLATE_MSG)

        created_ticket = mgr.create_ticket(
            title=args.get('--title'),
            body=body,
            subject=args.get('--subject'))
        return get_ticket_results(mgr, created_ticket['id'])
