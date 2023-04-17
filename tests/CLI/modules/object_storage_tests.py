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
        accounts = self.set_mock('SoftLayer_Network_Storage_Hub_Cleversafe_Account', 'getEndpoints')
        accounts.return_value = [
            {
                'legacy': False,
                'region': 'us-geo',
                'type': 'public',
                'url': 's3.us.cloud-object-storage.appdomain.cloud'
            },
            {
                'legacy': False,
                'region': 'us-geo',
                'type': 'private',
                'url': 's3.private.us.cloud-object-storage.appdomain.cloud'
            },
            {
                'legacy': True,
                'location': 'dal06',
                'region': 'regional',
                'type': 'public',
                'url': 's3.dal.cloud-object-storage.appdomain.cloud'
            },
            {
                'legacy': True,
                'location': 'ams03',
                'region': 'singleSite',
                'type': 'private',
                'url': 's3.ams.cloud-object-storage.appdomain.cloud'
            },
        ]

        result = self.run_command(['object-storage', 'endpoints', '123'])

        self.assert_no_fail(result)
        self.assertEqual(json.loads(result.output),
                         [{'Legacy': False,
                           'EndPoint Type': 'Cross Region',
                           'Public/Private': 'Public',
                           'Location/Region': 'us-geo',
                           'Url': 's3.us.cloud-object-storage.appdomain.cloud'},
                          {'Legacy': False,
                           'EndPoint Type': 'Cross Region',
                           'Public/Private': 'Private',
                           'Location/Region': 'us-geo',
                           'Url': 's3.private.us.cloud-object-storage.appdomain.cloud'},
                          {'Legacy': True,
                           'EndPoint Type': 'Region',
                           'Public/Private': 'Public',
                           'Location/Region': 'dal06',
                           'Url': 's3.dal.cloud-object-storage.appdomain.cloud'},
                          {'Legacy': True,
                           'EndPoint Type': 'Single Site',
                           'Public/Private': 'Private',
                           'Location/Region': 'ams03',
                           'Url': 's3.ams.cloud-object-storage.appdomain.cloud'}
                          ])

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
        self.assertEqual(result.output, 'true\n')

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

    def test_object_storage_cancel(self):
        result = self.run_command([
            '--really', 'object-storage', 'cancel', '1234'])

        self.assert_no_fail(result)
        self.assertEqual('Object storage with id 1234 has been marked'
                         ' for cancellation\n', result.output)
        self.assert_called_with('SoftLayer_Billing_Item', 'cancelItem',
                                args=(False, True, None))
