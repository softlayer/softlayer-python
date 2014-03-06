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
from SoftLayer.CLI import CLIRunnable, Table, \
    resolve_id, NestedDict, KeyValueTable

TEMPLATE_MSG = "***** SoftLayer Ticket Content ******"


def wrap_string(input_str):
    # utility method to wrap the content of the ticket,
    # as it can make the output messy
    return textwrap.wrap(input_str, 80)


def get_ticket_results(mgr, ticket_id, update_count=1):
    """ Get output about a ticket

    :param integer id: the ticket ID
    :param integer update_count: number of entries to retrieve from ticket
    :returns: a KeyValue table containing the details of the ticket

    """
    result = mgr.get_ticket(ticket_id)
    result = NestedDict(result)

    t = KeyValueTable(['Name', 'Value'])
    t.align['Name'] = 'r'
    t.align['Value'] = 'l'

    t.add_row(['id', result['id']])
    t.add_row(['title', result['title']])
    if result['assignedUser']:
        t.add_row(['assignedUser',
                   "%s %s" % (result['assignedUser']['firstName'],
                              result['assignedUser']['lastName'])])
    t.add_row(['createDate', result['createDate']])
    t.add_row(['lastEditDate', result['lastEditDate']])

    totalUpdates = len(result['updates'])
    count = min(totalUpdates, update_count)
    for index in range(0, count):
        i = totalUpdates - index
        update = wrap_string(result['updates'][i - 1]['entry'])
        t.add_row(['Update %s' % (i), update])

    return t


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
usage: sl ticket list [--open | --closed]

List tickets

Options:
  --open  display only open tickets
  --closed  display only closed tickets display all if none specified

"""
    action = 'list'

    def execute(self, args):
        ticket_mgr = TicketManager(self.client)

        tickets = ticket_mgr.list_tickets(
            openStatus=args.get('--open'),
            closedStatus=args.get('--closed'))

        t = Table(['id', 'assigned user', 'title',
                   'creation date', 'last edit date'])

        for ticket in tickets:
            if ticket['assignedUser']:
                t.add_row([
                    ticket['id'],
                    "%s %s" % (ticket['assignedUser']['firstName'],
                               ticket['assignedUser']['lastName']),
                    wrap_string(ticket['title']),
                    ticket['createDate'],
                    ticket['lastEditDate']
                ])
            else:
                t.add_row([
                    ticket['id'],
                    'N/A',
                    wrap_string(ticket['title']),
                    ticket['createDate'],
                    ticket['lastEditDate']
                ])

        return t


class ListSubjectsTickets(CLIRunnable):
    """
usage: sl ticket subjects

List Subject IDs for ticket creation

"""
    action = 'subjects'

    def execute(self, args):
        ticket_mgr = TicketManager(self.client)

        t = Table(['id', 'subject'])
        for subject in ticket_mgr.list_subjects():
                t.add_row([
                    subject['id'],
                    subject['name']
                ])
        return t


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

        mgr.update_ticket(t_id=ticket_id, body=body)
        return "Ticket Updated!"


class TicketsSummary(CLIRunnable):
    """
usage: sl ticket summary

Give summary info about tickets

"""
    action = 'summary'

    def execute(self, args):
        account = self.client['Account']
        mask = ('mask[openTicketCount, closedTicketCount, '
                'openBillingTicketCount, openOtherTicketCount, '
                'openSalesTicketCount, openSupportTicketCount, '
                'openAccountingTicketCount]')
        accountObject = account.getObject(mask=mask)
        t = Table(['Status', 'count'])

        nested = Table(['Type', 'count'])
        nested.add_row(['Accounting',
                        accountObject['openAccountingTicketCount']])
        nested.add_row(['Billing', accountObject['openBillingTicketCount']])
        nested.add_row(['Sales', accountObject['openSalesTicketCount']])
        nested.add_row(['Support', accountObject['openSupportTicketCount']])
        nested.add_row(['Other', accountObject['openOtherTicketCount']])
        nested.add_row(['Total', accountObject['openTicketCount']])
        t.add_row(['Open', nested])
        t.add_row(['Closed', accountObject['closedTicketCount']])

        return t


class TicketDetails(CLIRunnable):
    """
usage: sl ticket detail  <identifier> [options]

Get details for a ticket

Options:
  --updateCount=X  Show X count of updates [default: 1]
"""
    action = 'detail'

    def execute(self, args):
        mgr = TicketManager(self.client)

        ticket_id = resolve_id(
            mgr.resolve_ids, args.get('<identifier>'), 'ticket')

        count = args.get('--updateCount')
        return get_ticket_results(mgr, ticket_id, int(count))


class CreateTicket(CLIRunnable):
    """
usage: sl ticket create --title=TITLE --subject=<subjectID> [options]

Create a support ticket.

Required:
  --title=TITLE  The title of the ticket
  --subject=xxx  The id of the subject to use for the ticket,
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

        createdTicket = mgr.create_ticket(
            title=args.get('--title'),
            body=body,
            subject=args.get('--subject'))
        return get_ticket_results(mgr, createdTicket['id'], 1)
