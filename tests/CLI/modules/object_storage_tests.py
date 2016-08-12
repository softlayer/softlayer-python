"""
    SoftLayer.tests.CLI.modules.object_storage_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import json

from SoftLayer import testing


class ObjectStorageTests(testing.TestCase):

    def test_list_accounts(self):
        result = self.run_command(['object-storage', 'accounts'])

        self.assert_no_fail(result)
        self.assertEqual(json.loads(result.output),
                         [{'id': 12345, 'name': 'SLOS12345-1'},
                          {'id': 12346, 'name': 'SLOS12345-2'}])

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
