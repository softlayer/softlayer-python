"""
    SoftLayer.tests.CLI.modules.nas_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
from SoftLayer import testing

import json


class RWhoisTests(testing.TestCase):
    def test_list_nas(self):
        result = self.run_command(['nas', 'list'])

        self.assert_no_fail(result)
        self.assertEqual(json.loads(result.output),
                         [{'datacenter': 'Dallas',
                           'server': '127.0.0.1',
                           'id': 1,
                           'size': 10}])

    def test_nas_credentials(self):
        result = self.run_command(['nas', 'credentials', '12345'])
        self.assert_no_fail(result)
        self.assertEqual(json.loads(result.output),
                         [{
                             'password': '',
                             'username': 'username'
                         }])

    def test_server_credentials_exception_password_not_found(self):
        mock = self.set_mock('SoftLayer_Network_Storage', 'getObject')

        mock.return_value = {
            "accountId": 11111,
            "capacityGb": 20,
            "id": 22222,
            "nasType": "NAS",
            "serviceProviderId": 1,
            "username": "SL01SEV307",
            "credentials": []
        }

        result = self.run_command(['nas', 'credentials', '12345'])

        self.assertEqual(
            'None',
            str(result.exception)
        )
