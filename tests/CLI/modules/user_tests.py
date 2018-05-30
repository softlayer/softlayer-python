"""
    SoftLayer.tests.CLI.modules.user_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Tests for the user cli command
"""
from SoftLayer import testing

import json


class UserCLITests(testing.TestCase):

    """User list tests"""

    def test_user_list(self):
        result = self.run_command(['user', 'list'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Account', 'getUsers')

    def test_user_list_only_id(self):
        result = self.run_command(['user', 'list', '--columns=id'])
        self.assert_no_fail(result)
        self.assertEqual([{"id": 11100}, {"id": 11111}], json.loads(result.output))

    """User detail tests"""

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

    def test_detail_virtual(self):
        result = self.run_command(['user', 'detail', '11100', '-v'])
        self.assert_no_fail(result)
        self.assert_called_with(
            'SoftLayer_User_Customer', 'getObject', identifier=11100,
            mask='mask[id, virtualGuests]'
        )

    def test_detail_logins(self):
        result = self.run_command(['user', 'detail', '11100', '-l'])
        self.assert_no_fail(result)
        self.assert_called_with(
            'SoftLayer_User_Customer', 'getLoginAttempts', identifier=11100
        )

    def test_detail_events(self):
        result = self.run_command(['user', 'detail', '11100', '-e'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Event_Log', 'getAllObjects')

    """User permissions tests"""

    def test_permissions_list(self):
        result = self.run_command(['user', 'permissions', '11100'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_User_Customer_CustomerPermission_Permission', 'getAllObjects')
        self.assert_called_with(
            'SoftLayer_User_Customer', 'getObject', identifier=11100,
            mask='mask[id, permissions, isMasterUserFlag, roles]'
        )

    """User edit-permissions tests"""

    def test_edit_perms_on(self):
        result = self.run_command(['user', 'edit-permissions', '11100', '--enable', '-p', 'TEST'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_User_Customer', 'addBulkPortalPermission', identifier=11100)

    def test_edit_perms_on_bad(self):
        result = self.run_command(['user', 'edit-permissions', '11100', '--enable', '-p', 'TEST_NOt_exist'])
        self.assertEqual(result.exit_code, -1)

    def test_edit_perms_off(self):
        result = self.run_command(['user', 'edit-permissions', '11100', '--disable', '-p', 'TEST'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_User_Customer', 'removeBulkPortalPermission', identifier=11100)
