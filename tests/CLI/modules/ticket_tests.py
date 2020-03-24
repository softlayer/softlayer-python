"""
    SoftLayer.tests.CLI.modules.ticket_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import json
import mock

from SoftLayer.CLI import exceptions
from SoftLayer import testing


class TicketTests(testing.TestCase):

    def test_list(self):
        result = self.run_command(['ticket', 'list'])

        expected = [{
            'assigned_user': 'John Smith',
            'Case_Number': 'CS123456',
            'id': 102,
            'last_edited': '2013-08-01T14:16:47-07:00',
            'priority': 0,
            'status': 'Open',
            'title': 'Cloud Instance Cancellation - 08/01/13',
            'updates': 0}]
        self.assert_no_fail(result)
        self.assertEqual(expected, json.loads(result.output))

    def test_detail(self):
        result = self.run_command(['ticket', 'detail', '1'])

        expected = {
            'Case_Number': 'CS123456',
            'created': '2013-08-01T14:14:04-07:00',
            'edited': '2013-08-01T14:16:47-07:00',
            'id': 100,
            'priority': 'No Priority',
            'status': 'Closed',
            'title': 'Cloud Instance Cancellation - 08/01/13',
            'update 1': 'a bot says something',
            'update 2': 'By John Smith user says something',
            'update 3': 'By emp1 (Employee) employee says something',
        }
        self.assert_no_fail(result)
        self.assertEqual(json.loads(result.output), expected)

    def test_create(self):
        result = self.run_command(['ticket', 'create', '--title=Test',
                                   '--subject-id=1000',
                                   '--body=ticket body'])

        self.assert_no_fail(result)

        args = ({'subjectId': 1000,
                 'assignedUserId': 12345,
                 'title': 'Test'}, 'ticket body')

        self.assert_called_with('SoftLayer_Ticket', 'createStandardTicket', args=args)

    def test_create_with_priority(self):
        result = self.run_command(['ticket', 'create', '--title=Test',
                                   '--subject-id=1000',
                                   '--body=ticket body',
                                   '--priority=1'])

        self.assert_no_fail(result)

        args = ({'subjectId': 1000,
                 'assignedUserId': 12345,
                 'title': 'Test',
                 'priority': 1}, 'ticket body')

        self.assert_called_with('SoftLayer_Ticket', 'createStandardTicket', args=args)

    def test_create_and_attach(self):
        result = self.run_command(['ticket', 'create', '--title=Test',
                                   '--subject-id=1000',
                                   '--body=ticket body',
                                   '--hardware=234',
                                   '--virtual=567'])

        self.assert_no_fail(result)

        args = ({'subjectId': 1000,
                 'assignedUserId': 12345,
                 'title': 'Test'}, 'ticket body')

        self.assert_called_with('SoftLayer_Ticket', 'createStandardTicket',
                                args=args)
        self.assert_called_with('SoftLayer_Ticket', 'addAttachedHardware',
                                args=(234,),
                                identifier=100)
        self.assert_called_with('SoftLayer_Ticket', 'addAttachedVirtualGuest',
                                args=(567,),
                                identifier=100)

    @mock.patch('click.edit')
    def test_create_no_body(self, edit_mock):
        edit_mock.return_value = 'ticket body'
        result = self.run_command(['ticket', 'create', '--title=Test',
                                   '--subject-id=1000'])
        self.assert_no_fail(result)

        args = ({'subjectId': 1000,
                 'assignedUserId': 12345,
                 'title': 'Test'}, 'ticket body')

        self.assert_called_with('SoftLayer_Ticket', 'createStandardTicket',
                                args=args)

    def test_subjects(self):
        list_expected_ids = [1001, 1002, 1003, 1004, 1005]
        result = self.run_command(['ticket', 'subjects'])

        self.assert_no_fail(result)
        results = json.loads(result.output)
        for result in results:
            self.assertIn(result['id'], list_expected_ids)

    def test_attach_no_identifier(self):
        result = self.run_command(['ticket', 'attach', '1'])

        self.assertEqual(result.exit_code, 2)
        self.assertIsInstance(result.exception, exceptions.ArgumentError)

    def test_attach_two_identifiers(self):
        result = self.run_command(['ticket',
                                   'attach',
                                   '1',
                                   '--hardware=100',
                                   '--virtual=100'])

        self.assertEqual(result.exit_code, 2)
        self.assertIsInstance(result.exception, exceptions.ArgumentError)

    def test_ticket_attach_hardware(self):
        result = self.run_command(['ticket', 'attach', '1', '--hardware=100'])

        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Ticket', 'addAttachedHardware',
                                args=(100,),
                                identifier=1)

    def test_ticket_attach_virtual_server(self):
        result = self.run_command(['ticket', 'attach', '1', '--virtual=100'])

        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Ticket', 'addAttachedVirtualGuest',
                                args=(100,),
                                identifier=1)

    def test_detach_no_identifier(self):
        result = self.run_command(['ticket', 'detach', '1'])

        self.assertEqual(result.exit_code, 2)
        self.assertIsInstance(result.exception, exceptions.ArgumentError)

    def test_detach_two_identifiers(self):
        result = self.run_command(['ticket',
                                   'detach',
                                   '1',
                                   '--hardware=100',
                                   '--virtual=100'])
        self.assertEqual(result.exit_code, 2)
        self.assertIsInstance(result.exception, exceptions.ArgumentError)

    def test_ticket_detach_hardware(self):
        result = self.run_command(['ticket', 'detach', '1', '--hardware=100'])

        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Ticket',
                                'removeAttachedHardware',
                                args=(100,),
                                identifier=1)

    def test_ticket_detach_virtual_server(self):
        result = self.run_command(['ticket', 'detach', '1', '--virtual=100'])

        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Ticket',
                                'removeAttachedVirtualGuest',
                                args=(100,),
                                identifier=1)

    def test_ticket_upload_no_path(self):
        result = self.run_command(['ticket', 'upload', '1'])

        self.assertEqual(result.exit_code, 2)
        self.assertIsInstance(result.exception, exceptions.ArgumentError)

    def test_ticket_upload_invalid_path(self):
        result = self.run_command(['ticket', 'upload', '1',
                                   '--path=tests/resources/nonexistent_file',
                                   '--name=a_file_name'])

        self.assertEqual(result.exit_code, 2)
        self.assertIsInstance(result.exception, exceptions.ArgumentError)

    def test_ticket_upload_no_name(self):
        result = self.run_command(['ticket', 'upload', '1',
                                   '--path=tests/resources/attachment_upload'])

        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Ticket',
                                'addAttachedFile',
                                args=({"filename": "attachment_upload",
                                       "data": b"ticket attached data"},),
                                identifier=1)

    def test_ticket_json(self):
        result = self.run_command(['--format=json', 'ticket', 'detail', '1'])
        expected = {'Case_Number': 'CS123456',
                    'created': '2013-08-01T14:14:04-07:00',
                    'edited': '2013-08-01T14:16:47-07:00',
                    'id': 100,
                    'priority': 'No Priority',
                    'status': 'Closed',
                    'title': 'Cloud Instance Cancellation - 08/01/13',
                    'update 1': 'a bot says something',
                    'update 2': 'By John Smith user says something',
                    'update 3': 'By emp1 (Employee) employee says something'}
        self.assert_no_fail(result)
        self.assertEqual(json.loads(result.output), expected)
