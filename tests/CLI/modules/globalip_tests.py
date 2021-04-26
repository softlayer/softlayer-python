"""
    SoftLayer.tests.CLI.modules.globalip_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
from unittest import mock as mock

from SoftLayer.CLI import exceptions
from SoftLayer import testing

import json


class DnsTests(testing.TestCase):

    def test_ip_assign(self):
        result = self.run_command(['globalip', 'assign', '1', '127.0.0.1'])

        self.assert_no_fail(result)
        self.assertEqual(result.output, "")

    @mock.patch('SoftLayer.CLI.formatting.no_going_back')
    def test_ip_cancel(self, no_going_back_mock):
        # Test using --really flag
        result = self.run_command(['--really', 'globalip', 'cancel', '1'])

        self.assert_no_fail(result)
        self.assertEqual(result.output, "")

        # Test with confirmation
        no_going_back_mock.return_value = True
        result = self.run_command(['globalip', 'cancel', '1'])

        self.assert_no_fail(result)
        self.assertEqual(result.output, "")

        # Test with confirmation and responding negatively
        no_going_back_mock.return_value = False
        result = self.run_command(['globalip', 'cancel', '1'])

        self.assertEqual(result.exit_code, 2)
        self.assertIsInstance(result.exception, exceptions.CLIAbort)

    def test_ip_list(self):
        result = self.run_command(['globalip', 'list', '--ip-version=v4'])

        self.assert_no_fail(result)
        self.assertEqual(json.loads(result.output),
                         [{'assigned': 'Yes',
                           'id': '200',
                           'ip': '127.0.0.1',
                           'target': '127.0.0.1 (example.com)'},
                          {'assigned': 'Yes',
                           'id': '201',
                           'ip': '127.0.0.1',
                           'target': '127.0.0.1 (example.com)'}])

        result = self.run_command(['globalip', 'list', '--ip-version=v6'])
        self.assertEqual(json.loads(result.output),
                         [{'assigned': 'Yes',
                           'id': '200',
                           'ip': '127.0.0.1',
                           'target': '127.0.0.1 (example.com)'},
                          {'assigned': 'Yes',
                           'id': '201',
                           'ip': '127.0.0.1',
                           'target': '127.0.0.1 (example.com)'}])

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_create(self, confirm_mock):
        confirm_mock.return_value = True
        result = self.run_command(['globalip', 'create', '-v6'])
        self.assert_no_fail(result)
        self.assertEqual(json.loads(result.output), [{
            "item": "this is a thing",
            "cost": "2.00"
        },
            {
                "item": "Total monthly cost",
                "cost": "2.00"
        }])

    def test_ip_unassign(self):
        result = self.run_command(['globalip', 'unassign', '1'])
        self.assert_no_fail(result)
        self.assertEqual(result.output, "")
