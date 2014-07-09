"""
    SoftLayer.tests.managers.ticket_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import mock

import SoftLayer
from SoftLayer import testing
from SoftLayer.testing import fixtures


class TicketTests(testing.TestCase):

    def set_up(self):
        self.client = testing.FixtureClient()
        self.ticket = SoftLayer.TicketManager(self.client)

    def test_list_tickets(self):
        mcall = mock.call(mask=mock.ANY)
        service = self.client['Account']

        list_expected_ids = [100, 101, 102]
        open_expected_ids = [102]
        closed_expected_ids = [100, 101]

        results = self.ticket.list_tickets()
        service.getTickets.assert_has_calls(mcall)
        for result in results:
            self.assertIn(result['id'], list_expected_ids)

        results = self.ticket.list_tickets(open_status=True,
                                           closed_status=True)
        service.getTickets.assert_has_calls(mcall)
        for result in results:
            self.assertIn(result['id'], list_expected_ids)

        results = self.ticket.list_tickets(open_status=True,
                                           closed_status=False)
        for result in results:
            self.assertIn(result['id'], open_expected_ids)

        results = self.ticket.list_tickets(open_status=False,
                                           closed_status=True)
        for result in results:
            self.assertIn(result['id'], closed_expected_ids)

    def test_list_subjects(self):
        list_expected_ids = [1001, 1002, 1003, 1004, 1005]

        results = self.ticket.list_subjects()
        for result in results:
            self.assertIn(result['id'], list_expected_ids)

    def test_get_instance(self):
        result = self.ticket.get_ticket(100)
        self.client['Ticket'].getObject.assert_called_once_with(
            id=100, mask=mock.ANY)
        self.assertEqual(fixtures.Ticket.getObject, result)

    def test_create_ticket(self):
        self.ticket.create_ticket(
            title="Cloud Instance Cancellation - 08/01/13",
            body="body",
            subject=1004)
        self.client['Ticket'].createStandardTicket.assert_called_once_with(
            {"assignedUserId": 12345,
             "contents": "body",
             "subjectId": 1004,
             "title": "Cloud Instance Cancellation - 08/01/13"}, "body")

    def test_update_ticket(self):
        # Test editing user data
        service = self.client['Ticket']

        # test a full update
        self.ticket.update_ticket(100, body='Update1')
        service.edit.assert_called_once_with(
            {
                "accountId": 1234,
                "assignedUserId": 12345,
                "createDate": "2013-08-01T14:14:04-07:00",
                "id": 100,
                "lastEditDate": "2013-08-01T14:16:47-07:00",
                "lastEditType": "AUTO",
                "modifyDate": "2013-08-01T14:16:47-07:00",
                "status": {
                    "id": 1002,
                    "name": "Closed"
                },
                "statusId": 1002,
                "title": "Cloud Instance Cancellation - 08/01/13"
            },
            'Update1',
            id=100)
