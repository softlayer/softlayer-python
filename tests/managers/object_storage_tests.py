"""
    SoftLayer.tests.managers.object_storage_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import SoftLayer
from SoftLayer import fixtures
from SoftLayer import SoftLayerError
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

    def test_list_endpoints_no_results(self):
        accounts = self.set_mock('SoftLayer_Account', 'getHubNetworkStorage')
        accounts.return_value = {
            'storageNodes': [],
        }
        endpoints = self.object_storage.list_endpoints()
        self.assertEqual(endpoints,
                         [])

    def test_create_credential(self):
        accounts = self.set_mock('SoftLayer_Network_Storage_Hub_Cleversafe_Account', 'credentialCreate')
        accounts.return_value = {
            "id": 1103123,
            "password": "nwUEUsx6PiEoN0B1Xe9z9hUCyXMkAF",
            "username": "XfHhBNBPlPdlWyaP",
            "type": {
                "name": "S3 Compatible Signature"
            }
        }
        credential = self.object_storage.create_credential(100)
        self.assertEqual(credential,
                         {
                             "id": 1103123,
                             "password": "nwUEUsx6PiEoN0B1Xe9z9hUCyXMkAF",
                             "username": "XfHhBNBPlPdlWyaP",
                             "type": {
                                 "name": "S3 Compatible Signature"
                             }
                         })

    def test_delete_credential(self):
        accounts = self.set_mock('SoftLayer_Network_Storage_Hub_Cleversafe_Account', 'credentialDelete')
        accounts.return_value = True

        credential = self.object_storage.delete_credential(100)
        self.assertEqual(credential, True)

    def test_limit_credential(self):
        accounts = self.set_mock('SoftLayer_Network_Storage_Hub_Cleversafe_Account', 'getCredentialLimit')
        accounts.return_value = 2

        credential = self.object_storage.limit_credential(100)
        self.assertEqual(credential, 2)

    def test_list_credential(self):
        credentials = self.object_storage.list_credential(100)
        self.assertIsInstance(credentials, list)
        self.assert_called_with('SoftLayer_Network_Storage_Hub_Cleversafe_Account',
                                'getCredentials',
                                identifier=100)

    def test_resolve_ids(self):
        accounts = self.set_mock('SoftLayer_Account', 'getHubNetworkStorage')
        accounts.return_value = [{'id': 12345, 'username': 'test'}]
        identifier = self.object_storage.resolve_ids('test')
        self.assertEqual(identifier, [12345])
        self.assert_called_with('SoftLayer_Account', 'getHubNetworkStorage')

    def test_resolve_ids_fail_multiple(self):
        accounts = self.set_mock('SoftLayer_Account', 'getHubNetworkStorage')
        accounts.return_value = [{'id': 12345, 'username': 'test'},
                                 {'id': 12345, 'username': 'test'}]
        self.assertRaises(SoftLayerError, self.object_storage.resolve_ids, 'test')

    def test_resolve_ids_fail_no_found(self):
        accounts = self.set_mock('SoftLayer_Account', 'getHubNetworkStorage')
        accounts.return_value = []
        self.assertRaises(SoftLayerError, self.object_storage.resolve_ids, 'test')
