"""
    SoftLayer.tests.CLI.modules.ticket_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
from SoftLayer import testing

import json


class TicketTests(testing.TestCase):

    def test_list(self):
        result = self.run_command(['ticket', 'list'])

        expected = [{
            'assigned_user': 'John Smith',
            'id': 102,
            'last_edited': '2013-08-01T14:16:47-07:00',
            'status': 'Open',
            'title': 'Cloud Instance Cancellation - 08/01/13'}]
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(json.loads(result.output), expected)

    def test_detail(self):
        result = self.run_command(['ticket', 'detail', '1'])

        expected = {
            'created': '2013-08-01T14:14:04-07:00',
            'edited': '2013-08-01T14:16:47-07:00',
            'id': 100,
            'status': 'Closed',
            'title': 'Cloud Instance Cancellation - 08/01/13',
            'update 1': 'a bot says something',
            'update 2': 'By John Smith\nuser says something',
            'update 3': 'By emp1 (Employee)\nemployee says something',
        }
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(json.loads(result.output), expected)
