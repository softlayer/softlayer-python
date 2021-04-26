"""
    SoftLayer.tests.CLI.modules.object_storage_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import json
from unittest import mock as mock

from SoftLayer import testing


class ObjectStorageTests(testing.TestCase):

    def test_list_accounts(self):
        result = self.run_command(['object-storage', 'accounts'])

        self.assert_no_fail(result)
        self.assertEqual(json.loads(result.output),
                         [{'apiType': 'S3', 'id': 12345, 'name': 'SLOS12345-1'},
                          {'apiType': 'Swift', 'id': 12346, 'name': 'SLOS12345-2'}]
                         )

    def test_list_endpoints(self):
        accounts = self.set_mock('SoftLayer_Account', 'getHubNetworkStorage')
        accounts.return_value = {
            'storageNodes': [{
                'datacenter': {'name': 'dal05'},
                'frontendIpAddress': 'https://dal05/auth/v1.0/',
                'backendIpAddress': 'https://dal05/auth/v1.0/'}
            ],
        }

        result = self.run_command(['object-storage', 'endpoints'])

        self.assert_no_fail(result)
        self.assertEqual(json.loads(result.output),
                         [{'datacenter': 'dal05',
                           'private': 'https://dal05/auth/v1.0/',
                           'public': 'https://dal05/auth/v1.0/'}])

    def test_create_credential(self):
        result = self.run_command(['object-storage', 'credential', 'create', '100'])
        self.assert_no_fail(result)

    @mock.patch('SoftLayer.CLI.helpers.resolve_id')
    def test_create_credential_by_username(self, resolve_id_mock):
        resolve_id_mock.return_value = 100
        result = self.run_command(['object-storage', 'credential', 'create', 'test'])
        self.assert_no_fail(result)

    def test_delete_credential(self):
        result = self.run_command(['object-storage', 'credential', 'delete', '-c', 100, '100'])
        self.assert_no_fail(result)
        self.assertEqual(result.output, 'True\n')

    @mock.patch('SoftLayer.CLI.helpers.resolve_id')
    def test_delete_credential_by_username(self, resolve_id_mock):
        resolve_id_mock.return_value = 100
        result = self.run_command(['object-storage', 'credential', 'delete', 'test'])
        self.assert_no_fail(result)

    def test_limit_credential(self):
        result = self.run_command(['object-storage', 'credential', 'limit', '100'])

        self.assert_no_fail(result)
        self.assertIn('limit', result.output)

    @mock.patch('SoftLayer.CLI.helpers.resolve_id')
    def test_limit_credential_by_username(self, resolve_id_mock):
        resolve_id_mock.return_value = 100
        result = self.run_command(['object-storage', 'credential', 'limit', 'test'])
        self.assert_no_fail(result)

    def test_list_credential(self):
        result = self.run_command(['object-storage', 'credential', 'list', '100'])
        self.assert_no_fail(result)

    @mock.patch('SoftLayer.CLI.helpers.resolve_id')
    def test_list_credential_by_username(self, resolve_id_mock):
        resolve_id_mock.return_value = 100
        result = self.run_command(['object-storage', 'credential', 'list', 'test'])
        self.assert_no_fail(result)
