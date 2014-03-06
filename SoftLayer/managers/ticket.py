"""
    SoftLayer.ticket
    ~~~~~~~~~~~~~~~
    Ticket Manager/helpers

    :license: MIT, see LICENSE for more details.
"""

from SoftLayer.utils import query_filter, IdentifierMixin, NestedDict


class TicketManager(IdentifierMixin, object):
    """
    Manages account Tickets

    :param SoftLayer.API.Client client: an API client instance
    """

    def __init__(self, client):
        self.client = client
        self.account = self.client['Account']
        self.ticket = self.client['Ticket']

    def list_tickets(self, open=True, closed=True, title=None,
                     userId=None, **kwargs):
        """ List all tickets

        :param boolean open: include open tickets
        :param boolean closed: include closed tickets
        :param string title: filter based on title
        :param dict \*\*kwargs: response-level arguments (limit, offset, etc.)
        """
        TICKET_MASK = ('id',
                       'accountId',
                       'title',
                       'createDate',
                       'lastEditDate',
                       'assignedUser[firstName, lastName]')



        if 'mask' not in kwargs:
            kwargs['mask'] = TICKET_MASK

        _filter = NestedDict(kwargs.get('filter') or {})
        if title:
            _filter['ticket']['title'] = query_filter(title)

        kwargs['filter'] = _filter.to_dict()

        call = 'getTickets'
        if not all([open, closed]):
            if open:
                print 'Open'
                call = 'getOpenTickets'
            elif closed:
                print 'Closed'
                call = 'getClosedTickets'

        func = getattr(self.account, call)
        return func(**kwargs)

    def list_subjects(self, **kwargs):
        """ List all tickets

        :param dict \*\*kwargs: response-level arguments (limit, offset, etc.)
        """
        return self.client['Ticket_Subject'].getAllObjects(**kwargs)

    def get_ticket(self, ticket_id):
        """ Get details about a ticket

        :param integer id: the ticket ID
        :returns: A dictionary containing a large amount of information about
                  the specified ticket.

        """
        mask = 'mask[id, title, assignedUser[firstName, lastName],'\
               'createDate,lastEditDate,updates[entry],updateCount]'
        return self.ticket.getObject(id=ticket_id, mask=mask)

    def create_ticket(self, title=None, body=None,
                      hardware=None, rootPassword=None, subject=None):
        """ Create a new ticket

        :param string title: title for the new ticket
        :param string body: body for the new ticket
        :param string hardware: id of the hardware to be assigned to the ticket
        """

        currentUser = self.account.getCurrentUser()
        new_ticket = {
            'subjectId': subject,
            'contents': body,
            'assignedUserId': currentUser['id'],
            'title': title,
        }
        # if (hardware is None):
        created_ticket = self.ticket.createStandardTicket(new_ticket, body)
        # else:
        #    created_ticket = \
        #        self.ticket.createStandardTicket(new_ticket,
        #                                         body, hardware, rootPassword)
        return created_ticket

    def update_ticket(self, t_id=None, body=None):
        """ Update a ticket

        :param string id: the id of the ticket to update
        :param string body: entry to update in the ticket
        """

        ticket = self.ticket.getObject(id=t_id)
        return self.ticket.edit(ticket, body, id=t_id)

