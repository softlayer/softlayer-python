"""
    SoftLayer.tests.CLI.modules.user_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Tests for the user cli command
"""
from SoftLayer import exceptions
from SoftLayer import testing

from pprint import pprint as pp
import json
import mock

class UserTests(testing.TestCase):

    def test_user_list(self):
        result = self.run_command(['user', 'list'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Account', 'getUsers')

    def test_user_list_only_id(self):
        result = self.run_command(['user', 'list', '--columns=id'])
        self.assert_no_fail(result)
        self.assertEqual([{"id":11100}, {"id":11111}], json.loads(result.output))


    def test_detail(self):
        result = self.run_command(['user', 'detail', '11100'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_User_Customer', 'getObject')

    def test_detail_keys(self):
        result = self.run_command(['user', 'detail', '11100', '-k'])
        self.assert_no_fail(result)
        self.assertIn('APIKEY', result.output)

    def test_detail_permissions(self):
        result = self.run_command(['user', 'detail', '11100', '-p'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_User_Customer', 'getPermissions')
        self.assertIn('ACCESS_ALL_HARDWARE', result.output)

    def test_detail_hardware(self):
        result = self.run_command(['user', 'detail', '11100', '-h'])
        self.assert_no_fail(result)
        self.assert_called_with(
            'SoftLayer_User_Customer', 'getObject', identifier=11100,
            mask='mask[id, hardware, dedicatedHosts]'
        )