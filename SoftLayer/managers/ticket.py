"""
    SoftLayer.ticket
    ~~~~~~~~~~~~~~~~
    Ticket Manager/helpers

    :license: MIT, see LICENSE for more details.
"""
from SoftLayer import utils


class TicketManager(utils.IdentifierMixin, object):
    """Manages SoftLayer support tickets.

    See product information here: https://www.ibm.com/cloud/support

    :param SoftLayer.API.BaseClient client: the client instance

    """

    def __init__(self, client):
        self.client = client
        self.account = self.client['Account']
        self.ticket = self.client['Ticket']

    def list_tickets(self, open_status=True, closed_status=True):
        """List all tickets.

        :param boolean open_status: include open tickets
        :param boolean closed_status: include closed tickets
        """
        mask = """mask[id, serviceProviderResourceId, title, assignedUser[firstName, lastName], priority,
                  createDate, lastEditDate, accountId, status, updateCount]"""

        call = 'getTickets'
        if not all([open_status, closed_status]):
            if open_status:
                call = 'getOpenTickets'
            elif closed_status:
                call = 'getClosedTickets'
            else:
                raise ValueError("open_status and closed_status cannot both be False")
        return self.client.call('Account', call, mask=mask, iter=True)

    def list_subjects(self):
        """List all ticket subjects."""
        return self.client['Ticket_Subject'].getAllObjects()

    def get_ticket(self, ticket_id):
        """Get details about a ticket.

        :param integer ticket_id: the ticket ID
        :returns: dict -- information about the specified ticket

        """
        mask = """mask[id, serviceProviderResourceId, title, assignedUser[firstName, lastName],status,
                  createDate,lastEditDate,updates[entry,editor],updateCount, priority]"""
        return self.ticket.getObject(id=ticket_id, mask=mask)

    def create_ticket(self, title=None, body=None, subject=None, priority=None):
        """Create a new ticket.

        :param string title: title for the new ticket
        :param string body: body for the new ticket
        :param integer subject: id of the subject to be assigned to the ticket
        :param integer priority: Value from 1 (highest) to 4 (lowest)
        """
        current_user = self.account.getCurrentUser()
        new_ticket = {
            'subjectId': subject,
            'assignedUserId': current_user['id'],
            'title': title,
        }
        if priority is not None:
            new_ticket['priority'] = int(priority)

        created_ticket = self.ticket.createStandardTicket(new_ticket, body)
        return created_ticket

    def update_ticket(self, ticket_id=None, body=None):
        """Update a ticket.

        :param integer ticket_id: the id of the ticket to update
        :param string body: entry to update in the ticket
        """
        return self.ticket.addUpdate({'entry': body}, id=ticket_id)

    def upload_attachment(self, ticket_id=None, file_path=None, file_name=None):
        """Upload an attachment to a ticket.

        :param integer ticket_id: the id of the ticket to upload the attachment to
        :param string file_path: The path of the attachment to be uploaded
        :param string file_name: The name of the attachment shown in the ticket
        :returns: dict -- The uploaded attachment
        """
        file_content = None
        with open(file_path, 'rb') as attached_file:
            file_content = attached_file.read()

        file_object = {
            "filename": file_name,
            "data": file_content
        }

        return self.ticket.addAttachedFile(file_object, id=ticket_id)

    def attach_hardware(self, ticket_id=None, hardware_id=None):
        """Attach hardware to a ticket.

        :param integer ticket_id: the id of the ticket to attach to
        :param integer hardware_id: the id of the hardware to attach

        :returns: dict -- The new ticket attachment
        """
        return self.ticket.addAttachedHardware(hardware_id, id=ticket_id)

    def attach_virtual_server(self, ticket_id=None, virtual_id=None):
        """Attach a virtual server to a ticket.

        :param integer ticket_id: the id of the ticket to attach to
        :param integer virtual_id: the id of the virtual server to attach

        :returns: dict -- The new ticket attachment
        """
        return self.ticket.addAttachedVirtualGuest(virtual_id, id=ticket_id)

    def detach_hardware(self, ticket_id=None, hardware_id=None):
        """Detach hardware from a ticket.

        :param ticket_id: the id of the ticket to detach from
        :param hardware_id: the id of the hardware to detach

        :returns: bool -- Whether the detachment was successful
        """
        return self.ticket.removeAttachedHardware(hardware_id, id=ticket_id)

    def detach_virtual_server(self, ticket_id=None, virtual_id=None):
        """Detach a virtual server from a ticket.

        :param ticket_id: the id of the ticket to detach from
        :param virtual_id: the id of the virtual server to detach

        :returns: bool -- Whether the detachment was successful
        """
        return self.ticket.removeAttachedVirtualGuest(virtual_id, id=ticket_id)
