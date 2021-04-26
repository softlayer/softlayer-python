"""
    SoftLayer.tests.managers.user_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import datetime

from unittest import mock as mock

import SoftLayer
from SoftLayer import exceptions
from SoftLayer import testing

real_datetime_class = datetime.datetime


def mock_datetime(target, datetime_module):
    """A way to use specific datetimes in tests. Just mocking datetime doesn't work because of pypy

    https://solidgeargroup.com/mocking-the-time
    """

    class DatetimeSubclassMeta(type):
        @classmethod
        def __instancecheck__(mcs, obj):
            return isinstance(obj, real_datetime_class)

    class BaseMockedDatetime(real_datetime_class):
        @classmethod
        def now(cls, tz=None):
            return target.replace(tzinfo=tz)

        @classmethod
        def utcnow(cls):
            return target

        @classmethod
        def today(cls):
            return target

    # Python2 & Python3-compatible metaclass
    MockedDatetime = DatetimeSubclassMeta('datetime', (BaseMockedDatetime,), {})

    return mock.patch.object(datetime_module, 'datetime', MockedDatetime)


class UserManagerTests(testing.TestCase):

    def set_up(self):
        self.manager = SoftLayer.UserManager(self.client)

    def test_list_user_defaults(self):
        self.manager.list_users()
        self.assert_called_with('SoftLayer_Account', 'getUsers', mask=mock.ANY)

    def test_list_user_mask(self):
        self.manager.list_users(objectmask="mask[id]")
        self.assert_called_with('SoftLayer_Account', 'getUsers', mask="mask[id]")

    def test_list_user_filter(self):
        test_filter = {'id': {'operation': 1234}}
        self.manager.list_users(objectfilter=test_filter)
        self.assert_called_with('SoftLayer_Account', 'getUsers', filter=test_filter)

    def test_get_user_default(self):
        self.manager.get_user(1234)
        self.assert_called_with('SoftLayer_User_Customer', 'getObject', identifier=1234,
                                mask="mask[userStatus[name], parent[id, username]]")

    def test_get_user_mask(self):
        self.manager.get_user(1234, objectmask="mask[id]")
        self.assert_called_with('SoftLayer_User_Customer', 'getObject', identifier=1234, mask="mask[id]")

    def test_get_all_permissions(self):
        self.manager.get_all_permissions()
        self.assert_called_with('SoftLayer_User_Customer_CustomerPermission_Permission', 'getAllObjects')

    def test_add_permissions(self):
        self.manager.add_permissions(1234, ['TEST'])
        expected_args = (
            [{'keyName': 'TEST'}],
        )
        self.assert_called_with('SoftLayer_User_Customer', 'addBulkPortalPermission',
                                args=expected_args, identifier=1234)

    def test_remove_permissions(self):
        self.manager.remove_permissions(1234, ['TEST'])
        expected_args = (
            [{'keyName': 'TEST'}],
        )
        self.assert_called_with('SoftLayer_User_Customer', 'removeBulkPortalPermission',
                                args=expected_args, identifier=1234)

    def test_get_logins_default(self):
        target = datetime.datetime(2018, 5, 15)
        with mock_datetime(target, datetime):
            self.manager.get_logins(1234)
            expected_filter = {
                'loginAttempts': {
                    'createDate': {
                        'operation': 'greaterThanDate',
                        'options': [{'name': 'date', 'value': ['04/15/2018 0:0:0']}]
                    }
                }
            }
            self.assert_called_with('SoftLayer_User_Customer', 'getLoginAttempts', filter=expected_filter)

    def test_get_events_default(self):
        target = datetime.datetime(2018, 5, 15)
        with mock_datetime(target, datetime):
            self.manager.get_events(1234)
            expected_filter = {
                'userId': {
                    'operation': 1234
                },
                'eventCreateDate': {
                    'operation': 'greaterThanDate',
                    'options': [{'name': 'date', 'value': ['2018-04-15T00:00:00']}]
                }
            }
            self.assert_called_with('SoftLayer_Event_Log', 'getAllObjects', filter=expected_filter)

    def test_get_events_empty(self):
        event_mock = self.set_mock('SoftLayer_Event_Log', 'getAllObjects')
        event_mock.return_value = None
        result = self.manager.get_events(1234)

        self.assert_called_with('SoftLayer_Event_Log', 'getAllObjects', filter=mock.ANY)
        self.assertEqual([{'eventName': 'No Events Found'}], result)

    @mock.patch('SoftLayer.managers.user.UserManager.get_user_permissions')
    def test_permissions_from_user(self, user_permissions):
        user_permissions.return_value = [
            {"keyName": "TICKET_VIEW"},
            {"keyName": "TEST"}
        ]
        removed_permissions = [
            {'keyName': 'ACCESS_ALL_HARDWARE'},
            {'keyName': 'ACCESS_ALL_HARDWARE'},
            {'keyName': 'ACCOUNT_SUMMARY_VIEW'},
            {'keyName': 'ADD_SERVICE_STORAGE'},
            {'keyName': 'TEST_3'},
            {'keyName': 'TEST_4'}
        ]
        self.manager.permissions_from_user(1234, 5678)
        self.assert_called_with('SoftLayer_User_Customer', 'addBulkPortalPermission',
                                args=(user_permissions.return_value,))
        self.assert_called_with('SoftLayer_User_Customer', 'removeBulkPortalPermission',
                                args=(removed_permissions,))

    def test_get_id_from_username_one_match(self):
        account_mock = self.set_mock('SoftLayer_Account', 'getUsers')
        account_mock.return_value = [{'id': 1234}]
        user_id = self.manager._get_id_from_username('testUser')
        expected_filter = {'users': {'username': {'operation': '_= testUser'}}}
        self.assert_called_with('SoftLayer_Account', 'getUsers', filter=expected_filter, mask="mask[id, username]")
        self.assertEqual([1234], user_id)

    def test_get_id_from_username_multiple_match(self):
        account_mock = self.set_mock('SoftLayer_Account', 'getUsers')
        account_mock.return_value = [{'id': 1234}, {'id': 4567}]
        self.assertRaises(exceptions.SoftLayerError, self.manager._get_id_from_username, 'testUser')

    def test_get_id_from_username_zero_match(self):
        account_mock = self.set_mock('SoftLayer_Account', 'getUsers')
        account_mock.return_value = []
        self.assertRaises(exceptions.SoftLayerError, self.manager._get_id_from_username, 'testUser')

    def test_format_permission_object(self):
        result = self.manager.format_permission_object(['TEST'])
        self.assert_called_with('SoftLayer_User_Customer_CustomerPermission_Permission', 'getAllObjects')
        self.assertEqual([{'keyName': 'TEST'}], result)

    def test_format_permission_object_all(self):
        expected = [
            {'key': 'T_2', 'keyName': 'TEST', 'name': 'A Testing Permission'},
            {'key': 'T_1', 'keyName': 'TICKET_VIEW', 'name': 'View Tickets'}
        ]
        service_name = 'SoftLayer_User_Customer_CustomerPermission_Permission'
        permission_mock = self.set_mock(service_name, 'getAllObjects')
        permission_mock.return_value = expected
        result = self.manager.format_permission_object(['ALL'])
        self.assert_called_with(service_name, 'getAllObjects')
        self.assertEqual(expected, result)

    def test_get_current_user(self):
        result = self.manager.get_current_user()
        self.assert_called_with('SoftLayer_Account', 'getCurrentUser', mask=mock.ANY)
        self.assertEqual(result['id'], 12345)

    def test_get_current_user_mask(self):
        result = self.manager.get_current_user(objectmask="mask[id]")
        self.assert_called_with('SoftLayer_Account', 'getCurrentUser', mask="mask[id]")
        self.assertEqual(result['id'], 12345)

    def test_create_user_handle_paas_exception(self):
        user_template = {"username": "foobar", "email": "foobar@example.com"}

        self.manager.user_service = mock.Mock()

        # FaultCode IS NOT SoftLayer_Exception_User_Customer_DelegateIamIdInvitationToPaas
        any_error = exceptions.SoftLayerAPIError("SoftLayer_Exception_User_Customer",
                                                 "This exception indicates an error")

        self.manager.user_service.createObject.side_effect = any_error

        try:
            self.manager.create_user(user_template, "Pass@123")
        except exceptions.SoftLayerAPIError as ex:
            self.assertEqual(ex.faultCode, "SoftLayer_Exception_User_Customer")
            self.assertEqual(ex.faultString, "This exception indicates an error")

        # FaultCode is SoftLayer_Exception_User_Customer_DelegateIamIdInvitationToPaas
        paas_error = exceptions.SoftLayerAPIError("SoftLayer_Exception_User_Customer_DelegateIamIdInvitationToPaas",
                                                  "This exception does NOT indicate an error")

        self.manager.user_service.createObject.side_effect = paas_error

        try:
            self.manager.create_user(user_template, "Pass@123")
        except exceptions.SoftLayerError as ex:
            self.assertEqual(ex.args[0], "Your request for a new user was received, but it needs to be processed by "
                                         "the Platform Services API first. Barring any errors on the Platform Services "
                                         "side, your new user should be created shortly.")

    def test_vpn_manual(self):
        user_id = 1234
        self.manager.vpn_manual(user_id, True)
        self.assert_called_with('SoftLayer_User_Customer', 'editObject', identifier=user_id)

    def test_vpn_subnet_add(self):
        user_id = 1234
        subnet_id = 1234
        expected_args = (
            [{"userId": user_id, "subnetId": subnet_id}],
        )
        self.manager.vpn_subnet_add(user_id, [subnet_id])
        self.assert_called_with('SoftLayer_Network_Service_Vpn_Overrides', 'createObjects', args=expected_args)
        self.assert_called_with('SoftLayer_User_Customer', 'updateVpnUser', identifier=user_id)

    def test_vpn_subnet_remove(self):
        user_id = 1234
        subnet_id = 1234
        overrides = [{'id': 3661234, 'subnetId': subnet_id}]
        expected_args = (
            overrides,
        )
        self.manager.vpn_subnet_remove(user_id, [subnet_id])
        self.assert_called_with('SoftLayer_Network_Service_Vpn_Overrides', 'deleteObjects', args=expected_args)
        self.assert_called_with('SoftLayer_User_Customer', 'updateVpnUser', identifier=user_id)

    def test_get_all_notifications(self):
        self.manager.get_all_notifications()
        self.assert_called_with('SoftLayer_Email_Subscription', 'getAllObjects')

    def test_enable_notifications(self):
        self.manager.enable_notifications(['Test notification'])
        self.assert_called_with('SoftLayer_Email_Subscription', 'enable', identifier=111)

    def test_disable_notifications(self):
        self.manager.disable_notifications(['Test notification'])
        self.assert_called_with('SoftLayer_Email_Subscription', 'disable', identifier=111)

    def test_enable_notifications_fail(self):
        notification = self.set_mock('SoftLayer_Email_Subscription', 'enable')
        notification.return_value = False
        result = self.manager.enable_notifications(['Test notification'])
        self.assert_called_with('SoftLayer_Email_Subscription', 'enable', identifier=111)
        self.assertFalse(result)

    def test_disable_notifications_fail(self):
        notification = self.set_mock('SoftLayer_Email_Subscription', 'disable')
        notification.return_value = False
        result = self.manager.disable_notifications(['Test notification'])
        self.assert_called_with('SoftLayer_Email_Subscription', 'disable', identifier=111)
        self.assertFalse(result)

    def test_gather_notifications(self):
        expected_result = [
            {'description': 'Testing description.',
             'enabled': True,
             'id': 111,
             'name': 'Test notification'
             }
        ]
        result = self.manager.gather_notifications(['Test notification'])
        self.assert_called_with('SoftLayer_Email_Subscription',
                                'getAllObjects',
                                mask='mask[enabled]')
        self.assertEqual(result, expected_result)

    def test_gather_notifications_fail(self):
        ex = self.assertRaises(SoftLayer.SoftLayerError,
                               self.manager.gather_notifications,
                               ['Test not exit'])
        self.assertEqual("Test not exit is not a valid notification name", str(ex))
