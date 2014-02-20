"""
usage: sl ticket [<command>] [<args>...] [options]

Manage account tickets

The available commands are:
  create  Create a new ticket
  detail  Output details about an ticket
  list    List tickets
  update  Update an existing ticket
  subjects List the subject IDs that can be used for ticket creation
  summary Gives summary info about tickets
"""
# :license: MIT, see LICENSE for more details.

import textwrap

from SoftLayer import TicketManager
from SoftLayer.CLI import CLIRunnable, Table, resolve_id, NestedDict, KeyValueTable

""" Global variables for the status of the ticket - either open or closed """
OPEN = 'open'
CLOSED = 'closed'


class ListTickets(CLIRunnable):
    """
    usage: sl ticket list [--status=open,closed]

    List tickets

    Options:
      --status=open or closed  Display only opened or closed tickets, otherwise display both

    """
    action = 'list'

    def execute(self, args):
        ticket_mgr = TicketManager(self.client)

        mask = 'id,accountId,title,createDate,lastEditDate,assignedUser[firstName, lastName]'

        """Determine what needs to be returned, either open tickets, closed tickets, or both"""
        neither = True
        if (args.get('--status') == OPEN) or (args.get('--status') == CLOSED):
            neither = False

        tickets = []
        if (args.get('--status') == OPEN) or neither:
            for ticket in ticket_mgr.list_tickets(status=OPEN, mask=mask):
                tickets.append(ticket)

        if (args.get('--status') == CLOSED) or neither:
            for ticket in ticket_mgr.list_tickets(status=CLOSED, mask=mask):
                tickets.append(ticket)

        t = Table(['id', 'assigned user', 'title', 'creation date', 'last edit date'])

        for ticket in tickets:
            if ticket['assignedUser']:
                t.add_row([
                    ticket['id'],
                    ticket['assignedUser']['firstName'] + " " + ticket['assignedUser']['lastName'],
                    TicketUtils.wrap_string(ticket['title']),
                    ticket['createDate'],
                    ticket['lastEditDate']
                ])
            else:
                t.add_row([
                    ticket['id'],
                    'N/A',
                    TicketUtils.wrap_string(ticket['title']),
                    ticket['createDate'],
                    ticket['lastEditDate']
                ])

        return t


class ListSubjectsTickets(CLIRunnable):
    """
    usage: sl ticket subjects

    List Subject Ids for ticket creation

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
        if (body is None):
            body = TicketUtils.open_editor(beg_msg="***** Softlayer Ticket Content ******")

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
        accountObject = account.getObject(mask='mask[openTicketCount, closedTicketCount, openBillingTicketCount,openOtherTicketCount,openSalesTicketCount,openSupportTicketCount,openAccountingTicketCount]')
        t = Table(['Status', 'count'])

        nested = Table(['Type', 'count'])
        nested.add_row(['Accounting', accountObject['openAccountingTicketCount']])
        nested.add_row(['Billing', accountObject['openBillingTicketCount']])
        nested.add_row(['Sales', accountObject['openSalesTicketCount']])
        nested.add_row(['Support', accountObject['openSupportTicketCount']])
        nested.add_row(['Other', accountObject['openOtherTicketCount']])
        nested.add_row(['Total', accountObject['openTicketCount']])
        t.add_row(['Open', nested])
        t.add_row(['Closed', accountObject['closedTicketCount']])

        return t


class TicketUtils:
    """
    TicketUtils class that is a helper for common methods within the Ticket module.
    """

    @staticmethod
    def get_ticket_results(mgr, ticket_id, update_count=1, **kwargs):
        """ Get output about a ticket

        :param integer id: the ticket ID
        :param integer update_count: the number of entries to retrieve from the ticket
        :returns: a KeyValue table containing the details of the ticket

        """
        result = mgr.get_ticket(ticket_id)
        result = NestedDict(result)

        t = KeyValueTable(['Name', 'Value'])
        t.align['Name'] = 'r'
        t.align['Value'] = 'l'

        t.add_row(['id', result['id']])
        t.add_row(['title', result['title']])
        if (result['assignedUser']):
            t.add_row(['assignedUser', result['assignedUser']['firstName'] + " " + result['assignedUser']['lastName']])
        t.add_row(['createDate', result['createDate']])
        t.add_row(['lastEditDate', result['lastEditDate']])

        totalUpdates = len(result['updates'])
        count = min(totalUpdates, update_count)
        for index in range(0, count):
            t.add_row(['Update %s' % (totalUpdates - index), TicketUtils.wrap_string(result['updates'][totalUpdates - 1 - index]['entry'])])

        return t

    @staticmethod
    def open_editor(beg_msg, ending_msg=None):
        """

        :param beg_msg: generic msg to be appended at the end of the file
        :param ending_msg: placeholder msg to be appended at the end of the file, like filesystem info, etc, not being used now
        :returns: the content the user has entered

        """
        import tempfile
        import os
        from subprocess import call

        #Let's get the default EDITOR of the environment, use nano if none is specified
        editor = os.environ.get('EDITOR', 'nano')

        with tempfile.NamedTemporaryFile(suffix=".tmp") as tempfile:
            #populate the file with the baked messages
            tempfile.write("\n")
            tempfile.write(beg_msg)
            if (ending_msg):
                tempfile.write("\n")
                tempfile.write(ending_msg)
            #flush the file and open it for editing
            tempfile.flush()
            call([editor, tempfile.name])
            tempfile.seek(0)
            data = tempfile.read()
            return data

        return

    @staticmethod
    def wrap_string(input_str):
        #utility method to wrap the content of the ticket, as it can make the output messy
        return textwrap.wrap(input_str, 80)


class TicketDetails(CLIRunnable):
    """
    usage: sl ticket detail  <identifier> [options]

    Get details for a ticket

    Options:
      --updateCount=X  Show X count of updates, default is 1
    """
    action = 'detail'

    def execute(self, args):
        mgr = TicketManager(self.client)

        ticket_id = resolve_id(
            mgr.resolve_ids, args.get('<identifier>'), 'ticket')

        count = args.get('--updateCount')
        if not count:
            count = 1
        return TicketUtils.get_ticket_results(mgr, ticket_id, int(count))


class CreateTicket(CLIRunnable):
    """
    usage: sl ticket create --subject=xxx [options]

    Create a support ticket.

    Required:
      --title=TITLE  The title of the ticket
      --subject=xxx The id of the subject to use for the ticket, issue 'sl ticket subjects' to get the list

    Optional:
      --body the body text to attach to the ticket
    """
    action = 'create'
    required_params = ['--title, --subject']

    def execute(self, args):
        mgr = TicketManager(self.client)
        if (args.get('--title') is None):
            return 'Please provide a valid title'
        body = args.get('--body')
        if (body is None):
            body = TicketUtils.open_editor(beg_msg="***** Softlayer Ticket Content ******")

        createdTicket = mgr.create_ticket(
            title=(args.get('--title')),
            body=body,
            hardware=args.get('--hardware'),  # not being used now
            rootPassword=args.get('--rootPassword'),  # not being used now
            subject=args.get('--subject'))
        return TicketUtils.get_ticket_results(mgr, createdTicket['id'], 1)
