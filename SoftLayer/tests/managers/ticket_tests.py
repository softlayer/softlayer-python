"""
    SoftLayer.tests.managers.ticket_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import SoftLayer
from SoftLayer import testing
from SoftLayer.testing import fixtures


class TicketTests(testing.TestCase):

    def set_up(self):
        self.ticket = SoftLayer.TicketManager(self.client)

    def test_list_tickets(self):
        results = self.ticket.list_tickets()

        for result in results:
            self.assertIn(result['id'], [100, 101, 102])
        self.assert_called_with('SoftLayer_Account', 'getTickets')

    def test_list_tickets_all(self):
        results = self.ticket.list_tickets(open_status=True,
                                           closed_status=True)

        for result in results:
            self.assertIn(result['id'], [100, 101, 102])
        self.assert_called_with('SoftLayer_Account', 'getTickets')

    def test_list_tickets_open(self):
        results = self.ticket.list_tickets(open_status=True,
                                           closed_status=False)
        for result in results:
            self.assertIn(result['id'], [102])
        self.assert_called_with('SoftLayer_Account', 'getOpenTickets')

    def test_list_tickets_closed(self):
        results = self.ticket.list_tickets(open_status=False,
                                           closed_status=True)
        for result in results:
            self.assertIn(result['id'], [100, 101])
        self.assert_called_with('SoftLayer_Account', 'getClosedTickets')

    def test_list_subjects(self):
        list_expected_ids = [1001, 1002, 1003, 1004, 1005]

        results = self.ticket.list_subjects()
        for result in results:
            self.assertIn(result['id'], list_expected_ids)

    def test_get_instance(self):
        result = self.ticket.get_ticket(100)

        self.assertEqual(result, fixtures.SoftLayer_Ticket.getObject)
        self.assert_called_with('SoftLayer_Ticket', 'getObject',
                                identifier=100)

    def test_create_ticket(self):
        self.ticket.create_ticket(
            title="Cloud Instance Cancellation - 08/01/13",
            body="body",
            subject=1004)

        args = ({"assignedUserId": 12345,
                 "contents": "body",
                 "subjectId": 1004,
                 "title": "Cloud Instance Cancellation - 08/01/13"},
                "body")
        self.assert_called_with('SoftLayer_Ticket', 'createStandardTicket',
                                args=args)

    def test_update_ticket(self):
        # test a full update
        self.ticket.update_ticket(100, body='Update1')
        self.assert_called_with('SoftLayer_Ticket', 'addUpdate',
                                args=({'entry': 'Update1'},),
                                identifier=100)
