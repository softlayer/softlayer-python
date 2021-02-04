"""
    SoftLayer.tests.CLI.modules.object_storage_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import json
from unittest import mock

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
        accounts = self.set_mock('SoftLayer_Network_Storage_Hub_Cleversafe_Account', 'credentialCreate')
        accounts.return_value = {
            "accountId": "12345",
            "createDate": "2019-04-05T13:25:25-06:00",
            "id": 11111,
            "password": "nwUEUsx6PiEoN0B1Xe9z9hUCy",
            "username": "XfHhBNBPlPdl",
            "type": {
                "description": "A credential for generating S3 Compatible Signatures.",
                "keyName": "S3_COMPATIBLE_SIGNATURE",
                "name": "S3 Compatible Signature"
            }
        }

        result = self.run_command(['object-storage', 'credential', 'create', '100'])

        self.assert_no_fail(result)
        self.assertEqual(json.loads(result.output),
                         [{'id': 11111,
                           'password': 'nwUEUsx6PiEoN0B1Xe9z9hUCy',
                           'type_name': 'S3 Compatible Signature',
                           'username': 'XfHhBNBPlPdl'}]
                         )

    def test_delete_credential(self):
        accounts = self.set_mock('SoftLayer_Network_Storage_Hub_Cleversafe_Account', 'credentialDelete')
        accounts.return_value = True

        result = self.run_command(['object-storage', 'credential', 'delete', '-c', 100, '100'])

        self.assert_no_fail(result)
        self.assertEqual(result.output, 'True\n')

    def test_limit_credential(self):
        accounts = self.set_mock('SoftLayer_Network_Storage_Hub_Cleversafe_Account', 'getCredentialLimit')
        accounts.return_value = 2

        result = self.run_command(['object-storage', 'credential', 'limit', '100'])

        self.assert_no_fail(result)
        self.assertEqual(json.loads(result.output), [{'limit': 2}])

    def test_list_credential(self):
        result = self.run_command(['object-storage', 'credential', 'list', '100'])
        self.assert_no_fail(result)

    @mock.patch('SoftLayer.CLI.helpers.resolve_id')
    def test_list_credential_by_username(self, resolve_id_mock):
        resolve_id_mock.return_value = 100
        result = self.run_command(['object-storage', 'credential', 'list', 'test'])
        self.assert_no_fail(result)
