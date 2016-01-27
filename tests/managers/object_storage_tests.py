"""
    SoftLayer.tests.managers.object_storage_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import SoftLayer
from SoftLayer import fixtures
from SoftLayer import testing


class ObjectStorageTests(testing.TestCase):

    def set_up(self):
        self.object_storage = SoftLayer.ObjectStorageManager(self.client)

    def test_list_accounts(self):
        accounts = self.object_storage.list_accounts()
        self.assertEqual(accounts,
                         fixtures.SoftLayer_Account.getHubNetworkStorage)

    def test_list_endpoints(self):
        accounts = self.set_mock('SoftLayer_Account', 'getHubNetworkStorage')
        accounts.return_value = {
            'storageNodes': [{
                'datacenter': {'name': 'dal05'},
                'frontendIpAddress': 'https://dal05/auth/v1.0/',
                'backendIpAddress': 'https://dal05/auth/v1.0/'}
            ],
        }
        endpoints = self.object_storage.list_endpoints()
        self.assertEqual(endpoints,
                         [{'datacenter': {'name': 'dal05'},
                           'private': 'https://dal05/auth/v1.0/',
                           'public': 'https://dal05/auth/v1.0/'}])
