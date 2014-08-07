"""
    SoftLayer.ticket
    ~~~~~~~~~~~~~~~
    Ticket Manager/helpers

    :license: MIT, see LICENSE for more details.
"""

from SoftLayer import utils


class TicketManager(utils.IdentifierMixin, object):
    """
    Manages account Tickets

    :param SoftLayer.API.Client client: an API client instance
    """

    def __init__(self, client):
        self.client = client
        self.account = self.client['Account']
        self.ticket = self.client['Ticket']

    def list_tickets(self, open_status=True, closed_status=True):
        """ List all tickets

        :param boolean open_status: include open tickets
        :param boolean closed_status: include closed tickets
        """
        mask = ('mask[id, title, assignedUser[firstName, lastName],'
                'createDate,lastEditDate,accountId]')

        call = 'getTickets'
        if not all([open_status, closed_status]):
            if open_status:
                call = 'getOpenTickets'
            elif closed_status:
                call = 'getClosedTickets'

        func = getattr(self.account, call)
        return func(mask=mask)

    def list_subjects(self):
        """ List all tickets"""
        return self.client['Ticket_Subject'].getAllObjects()

    def get_ticket(self, ticket_id):
        """ Get details about a ticket

        :param integer id: the ticket ID
        :returns: A dictionary containing a large amount of information about
                  the specified ticket.

        """
        mask = ('mask[id, title, assignedUser[firstName, lastName],'
                'createDate,lastEditDate,updates[entry],updateCount]')
        return self.ticket.getObject(id=ticket_id, mask=mask)

    def create_ticket(self, title=None, body=None, subject=None):
        """ Create a new ticket

        :param string title: title for the new ticket
        :param string body: body for the new ticket
        :param integer subject: id of the subject to be assigned to the ticket
        """

        current_user = self.account.getCurrentUser()
        new_ticket = {
            'subjectId': subject,
            'contents': body,
            'assignedUserId': current_user['id'],
            'title': title,
        }
        created_ticket = self.ticket.createStandardTicket(new_ticket, body)
        return created_ticket

    def update_ticket(self, ticket_id=None, body=None):
        """ Update a ticket

        :param integer ticket_id: the id of the ticket to update
        :param string body: entry to update in the ticket
        """

        ticket = self.ticket.getObject(id=ticket_id)
        return self.ticket.edit(ticket, body, id=ticket_id)
