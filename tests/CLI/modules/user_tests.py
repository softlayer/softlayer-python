"""
    SoftLayer.tests.CLI.modules.user_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Tests for the user cli command
"""
import json
import sys
import unittest

from unittest import mock as mock

from SoftLayer import testing


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

    def test_print_hardware_access(self):
        mock = self.set_mock('SoftLayer_User_Customer', 'getObject')
        mock.return_value = {
            'accountId': 12345,
            'address1': '315 Test Street',
            'city': 'Houston',
            'companyName': 'SoftLayer Development Community',
            'country': 'US',
            'displayName': 'Test',
            'email': 'test@us.ibm.com',
            'firstName': 'Test',
            'id': 244956,
            'lastName': 'Testerson',
            'postalCode': '77002',
            'state': 'TX',
            'statusDate': None,
            'hardware': [
                {'id': 1234,
                 'fullyQualifiedDomainName': 'test.test.test',
                 'provisionDate': '2018-05-08T15:28:32-06:00',
                 'primaryBackendIpAddress': '175.125.126.118',
                 'primaryIpAddress': '175.125.126.118'}
            ],
            'dedicatedHosts': [
                {'id': 1234,
                 'fullyQualifiedDomainName': 'test.test.test',
                 'provisionDate': '2018-05-08T15:28:32-06:00',
                 'primaryBackendIpAddress': '175.125.126.118',
                 'primaryIpAddress': '175.125.126.118'}
            ],
        }
        result = self.run_command(['user', 'detail', '11100', '-h'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_User_Customer', 'getObject', identifier=11100,
                                mask="mask[id, hardware, dedicatedHosts]")

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
        self.assertEqual(result.exit_code, 1)

    def test_edit_perms_off(self):
        result = self.run_command(['user', 'edit-permissions', '11100', '--disable', '-p', 'TEST'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_User_Customer', 'removeBulkPortalPermission', identifier=11100)

    @mock.patch('SoftLayer.CLI.user.edit_permissions.click')
    def test_edit_perms_off_failure(self, click):
        permission_mock = self.set_mock('SoftLayer_User_Customer', 'removeBulkPortalPermission')
        permission_mock.return_value = False
        result = self.run_command(['user', 'edit-permissions', '11100', '--disable', '-p', 'TEST'])
        click.secho.assert_called_with('Failed to update permissions: TEST', fg='red')
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_User_Customer', 'removeBulkPortalPermission', identifier=11100)

    def test_edit_perms_from_user(self):
        result = self.run_command(['user', 'edit-permissions', '11100', '-u', '1234'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_User_Customer', 'getPermissions', identifier=1234)
        self.assert_called_with('SoftLayer_User_Customer', 'removeBulkPortalPermission', identifier=11100)
        self.assert_called_with('SoftLayer_User_Customer', 'addBulkPortalPermission', identifier=11100)

    """User create tests"""

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_create_user(self, confirm_mock):
        confirm_mock.return_value = True
        result = self.run_command(['user', 'create', 'test', '-e', 'test@us.ibm.com', '-p', 'testword'])
        self.assert_no_fail(result)
        self.assertIn('test@us.ibm.com', result.output)
        self.assert_called_with('SoftLayer_Account', 'getCurrentUser')
        self.assert_called_with('SoftLayer_User_Customer', 'createObject', args=mock.ANY)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_create_user_no_confirm(self, confirm_mock):
        confirm_mock.return_value = False
        result = self.run_command(['user', 'create', 'test', '-e', 'test@us.ibm.com', '-p', 'testword'])
        self.assertEqual(result.exit_code, 2)

    @unittest.skipIf(sys.version_info < (3, 6), "Secrets module only exists in version 3.6+")
    @mock.patch('secrets.choice')
    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_create_user_generate_password_36(self, confirm_mock, secrets):
        secrets.return_value = 'Q'
        confirm_mock.return_value = True
        result = self.run_command(['user', 'create', 'test', '-e', 'test@us.ibm.com', '-p', 'generate'])

        self.assert_no_fail(result)
        self.assertIn('test@us.ibm.com', result.output)
        self.assertIn('QQQQQQQQQQQQQQQQQQQQQQ', result.output)
        self.assert_called_with('SoftLayer_Account', 'getCurrentUser')
        self.assert_called_with('SoftLayer_User_Customer', 'createObject', args=mock.ANY)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_create_user_generate_password_2(self, confirm_mock):
        if sys.version_info >= (3, 6):
            self.skipTest("Python needs to be < 3.6 for this test.")

        confirm_mock.return_value = True
        result = self.run_command(['user', 'create', 'test', '-e', 'test@us.ibm.com', '-p', 'generate'])
        self.assertIn(result.output, "ImportError")

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_create_user_and_apikey(self, confirm_mock):
        confirm_mock.return_value = True
        result = self.run_command(['user', 'create', 'test', '-e', 'test@us.ibm.com'])
        self.assert_no_fail(result)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_create_user_with_template(self, confirm_mock):
        confirm_mock.return_value = True
        result = self.run_command(['user', 'create', 'test', '-e', 'test@us.ibm.com',
                                   '-t', '{"firstName": "Supermand"}'])
        self.assertIn('Supermand', result.output)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_create_user_with_bad_template(self, confirm_mock):
        confirm_mock.return_value = True
        result = self.run_command(['user', 'create', 'test', '-e', 'test@us.ibm.com',
                                   '-t', '{firstName: "Supermand"}'])
        self.assertIn("Argument Error", result.exception.message)
        self.assertEqual(result.exit_code, 2)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_create_user_with_no_confirm(self, confirm_mock):
        confirm_mock.return_value = False
        result = self.run_command(['user', 'create', 'test', '-e', 'test@us.ibm.com'])
        self.assertIn("Canceling creation!", result.exception.message)
        self.assertEqual(result.exit_code, 2)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_create_user_from_user(self, confirm_mock):
        confirm_mock.return_value = True
        result = self.run_command(['user', 'create', 'test', '-e', 'test@us.ibm.com', '-u', '1234'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_User_Customer', 'getObject', identifier=1234)

    """User edit-details tests"""

    @mock.patch('SoftLayer.CLI.user.edit_details.click')
    def test_edit_details(self, click):
        result = self.run_command(['user', 'edit-details', '1234', '-t', '{"firstName":"Supermand"}'])
        click.secho.assert_called_with('1234 updated successfully', fg='green')
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_User_Customer', 'editObject',
                                args=({'firstName': 'Supermand'},), identifier=1234)

    @mock.patch('SoftLayer.CLI.user.edit_details.click')
    def test_edit_details_failure(self, click):
        mock = self.set_mock('SoftLayer_User_Customer', 'editObject')
        mock.return_value = False
        result = self.run_command(['user', 'edit-details', '1234', '-t', '{"firstName":"Supermand"}'])
        click.secho.assert_called_with('Failed to update 1234', fg='red')
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_User_Customer', 'editObject',
                                args=({'firstName': 'Supermand'},), identifier=1234)

    def test_edit_details_bad_json(self):
        result = self.run_command(['user', 'edit-details', '1234', '-t', '{firstName:"Supermand"}'])
        self.assertIn("Argument Error", result.exception.message)
        self.assertEqual(result.exit_code, 2)

    """User delete tests"""

    @mock.patch('SoftLayer.CLI.user.delete.click')
    def test_delete(self, click):
        result = self.run_command(['user', 'delete', '12345'])
        click.secho.assert_called_with('12345 deleted successfully', fg='green')
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_User_Customer', 'editObject',
                                args=({'userStatusId': 1021},), identifier=12345)

    @mock.patch('SoftLayer.CLI.user.delete.click')
    def test_delete_failure(self, click):
        mock = self.set_mock('SoftLayer_User_Customer', 'editObject')
        mock.return_value = False
        result = self.run_command(['user', 'delete', '12345'])
        click.secho.assert_called_with('Failed to delete 12345', fg='red')
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_User_Customer', 'editObject',
                                args=({'userStatusId': 1021},), identifier=12345)

    """User vpn manual config tests"""

    @mock.patch('SoftLayer.CLI.user.vpn_manual.click')
    def test_vpn_manual(self, click):
        result = self.run_command(['user', 'vpn-manual', '12345', '--enable'])
        click.secho.assert_called_with('12345 vpn manual config enable', fg='green')
        self.assert_no_fail(result)

    def test_vpn_manual_fail(self):
        mock = self.set_mock('SoftLayer_User_Customer', 'editObject')
        mock.return_value = False
        result = self.run_command(['user', 'vpn-manual', '12345', '--enable'])
        self.assert_no_fail(result)

    """User vpn subnet tests"""

    @mock.patch('SoftLayer.CLI.user.vpn_subnet.click')
    def test_vpn_subnet_add(self, click):
        result = self.run_command(['user', 'vpn-subnet', '12345', '--add', '1234'])
        click.secho.assert_called_with('12345 updated successfully', fg='green')
        self.assert_no_fail(result)

    def test_vpn_subnet_add_fail(self):
        mock = self.set_mock('SoftLayer_Network_Service_Vpn_Overrides', 'createObjects')
        mock.return_value = False
        result = self.run_command(['user', 'vpn-subnet', '12345', '--add', '1234'])
        self.assert_no_fail(result)

    @mock.patch('SoftLayer.CLI.user.vpn_subnet.click')
    def test_vpn_subnet_remove(self, click):
        result = self.run_command(['user', 'vpn-subnet', '12345', '--remove', '1234'])
        click.secho.assert_called_with('12345 updated successfully', fg='green')
        self.assert_no_fail(result)

    """User notification tests"""

    def test_notificacions_list(self):
        result = self.run_command(['user', 'notifications'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Email_Subscription', 'getAllObjects', mask='mask[enabled]')

    """User edit-notification tests"""

    def test_edit_notification_on(self):
        result = self.run_command(['user', 'edit-notifications', '--enable', 'Test notification'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Email_Subscription', 'enable', identifier=111)

    def test_edit_notification_on_bad(self):
        result = self.run_command(['user', 'edit-notifications', '--enable', 'Test not exist'])
        self.assertEqual(result.exit_code, 1)

    def test_edit_notifications_off(self):
        result = self.run_command(['user', 'edit-notifications', '--disable', 'Test notification'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Email_Subscription', 'disable', identifier=111)

    @mock.patch('SoftLayer.CLI.user.edit_notifications.click')
    def test_edit_notification_off_failure(self, click):
        notification = self.set_mock('SoftLayer_Email_Subscription', 'disable')
        notification.return_value = False
        result = self.run_command(['user', 'edit-notifications', '--disable', 'Test notification'])
        click.secho.assert_called_with('Failed to update notifications: Test notification', fg='red')
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Email_Subscription', 'disable', identifier=111)
