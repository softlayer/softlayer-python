"""
    SoftLayer.tests.CLI.modules.globalip_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
from unittest import mock as mock

from SoftLayer.CLI import exceptions
from SoftLayer import testing

import json


class GlobalIpTests(testing.TestCase):

    @mock.patch('SoftLayer.CLI.formatting.confirm')
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
        self.assert_called_with('SoftLayer_Network_Subnet', 'clearRoute', identifier=9988)

    def test_ip_assign(self):
        result = self.run_command(['globalip', 'assign', '1', '999'])
        self.assert_no_fail(result)
        self.assertEqual(result.output, "")
        service = 'SoftLayer_Network_Subnet_IpAddress'
        self.assert_called_with('SoftLayer_Network_Subnet', 'route', identifier=9988, args=(service, '999'))

    def test_ip_assign_target(self):
        result = self.run_command(['globalip', 'assign', '1', '--target-id=8123'])
        self.assert_no_fail(result)
        self.assertEqual(result.output, "")
        service = 'SoftLayer_Network_Subnet_IpAddress'
        self.assert_called_with('SoftLayer_Network_Subnet', 'route', identifier=9988, args=(service, '8123'))

    def test_ip_assign_ip(self):
        mock_api = self.set_mock('SoftLayer_Account', 'getGlobalIpRecords')
        mock_api.return_value = [{"id": 112233}]
        result = self.run_command(['globalip', 'assign', '192.168.1.1', '1.2.3.4'])
        self.assert_no_fail(result)
        self.assertEqual(result.output, "")
        service = 'SoftLayer_Network_Subnet_IpAddress'
        self.assert_called_with(f"{service}_Global", "getObject", identifier=112233)
        self.assert_called_with('SoftLayer_Network_Subnet', 'route', identifier=9988, args=(service, '1.2.3.4'))

    def test_ip_cancel_force(self):
        result = self.run_command(['globalip', 'cancel', '1', '--force'])

        self.assert_no_fail(result)
        self.assertEqual(result.exit_code, 0)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_ip_cancel_no_abort(self, confirm_mock):
        # Test with confirmation and responding negatively
        confirm_mock.return_value = True
        result = self.run_command(['globalip', 'cancel', '1'])

        self.assert_no_fail(result)
        self.assertEqual(result.exit_code, 0)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_ip_cancel_abort(self, confirm_mock):
        # Test with confirmation and responding negatively
        confirm_mock.return_value = False
        result = self.run_command(['globalip', 'cancel', '1'])

        self.assertEqual(result.exit_code, 2)
        self.assertIsInstance(result.exception, exceptions.CLIAbort)
