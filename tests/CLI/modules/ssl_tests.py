"""
    SoftLayer.tests.CLI.modules.ssl_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    :license: MIT, see LICENSE for more details.
"""
from SoftLayer import testing

import json
from unittest import mock as mock


class SslTests(testing.TestCase):
    def test_list(self):
        result = self.run_command(['ssl', 'list', '--status', 'all'])
        self.assert_no_fail(result)
        self.assertEqual(json.loads(result.output), [
            {
                "id": 1234,
                "common_name": "cert",
                "days_until_expire": 0,
                "notes": None
            }
        ])

    @mock.patch('SoftLayer.CLI.formatting.no_going_back')
    def test_remove(self, confirm_mock):
        confirm_mock.return_value = True
        result = self.run_command(['ssl', 'remove', '123456'])
        self.assert_no_fail(result)
        self.assertEqual(result.exit_code, 0)

    def test_download(self):
        result = self.run_command(['ssl', 'download', '123456'])
        self.assert_no_fail(result)
        self.assertEqual(result.exit_code, 0)
