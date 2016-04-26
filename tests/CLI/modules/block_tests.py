"""
    SoftLayer.tests.CLI.modules.block_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
from SoftLayer import testing

import json


class BlockTests(testing.TestCase):

    def test_access_list(self):
        result = self.run_command(['block', 'access-list', '1234'])

        self.assertEqual(result.exit_code, 0)
        self.assertEqual([
            {
                'username': 'joe',
                'name': 'test-server.example.com',
                'type': 'VIRTUAL',
                'hostIqn': 'test-server',
                'password': '12345',
                'primaryBackendIpAddress': '10.0.0.1',
                'id': 1234,
            },
            {
                'username': 'joe',
                'name': 'test-server.example.com',
                'type': 'HARDWARE',
                'hostIqn': 'test-server',
                'password': '12345',
                'primaryBackendIpAddress': '10.0.0.2',
                'id': 1234,
            },
            {
                'username': 'joe',
                'name': '10.0.0.1/24 (backend subnet)',
                'type': 'SUBNET',
                'hostIqn': 'test-server',
                'password': '12345',
                'primaryBackendIpAddress': None,
                'id': 1234,
            },
            {
                'username': 'joe',
                'name': '10.0.0.1 (backend ip)',
                'type': 'IP',
                'hostIqn': 'test-server',
                'password': '12345',
                'primaryBackendIpAddress': None,
                'id': 1234,
            }],
            json.loads(result.output),)

    def test_volume_cancel(self):
        result = self.run_command([
            '--really', 'block', 'volume-cancel', '1234'])

        self.assertEqual(result.exit_code, 0)
        self.assertEqual("", result.output)
        self.assert_called_with('SoftLayer_Billing_Item', 'cancelItem',
                                args=(False, True, None))

    def test_volume_detail(self):
        result = self.run_command(['block', 'volume-detail', '1234'])

        self.assertEqual(result.exit_code, 0)
        self.assertEqual({
            'Username': 'username',
            'LUN Id': '2',
            'Endurance Tier': 'Tier 1',
            'IOPs': 1000,
            'Snapshot Capacity (GB)': 10,
            'Snapshot Used (Bytes)': 1024,
            'Capacity (GB)': '20GB',
            'Target IP': '10.1.2.3',
            'Data Center': 'dal05',
            'Type': 'ENDURANCE',
            'ID': 100,
        }, json.loads(result.output))

    def test_volume_list(self):
        result = self.run_command(['block', 'volume-list'])

        self.assertEqual(result.exit_code, 0)
        self.assertEqual([
            {
                'bytesUsed': None,
                'capacityGb': 20,
                'datacenter': None,
                'id': 100,
                'ipAddr': '10.1.2.3',
                'storageType': 'ENDURANCE',
                'username': 'username'
            }],
            json.loads(result.output))
