"""
    SoftLayer.tests.managers.user_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import mock
import SoftLayer
from SoftLayer import exceptions
from SoftLayer import testing


class UserTests(testing.TestCase):

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
        from datetime import date
        with mock.patch('SoftLayer.managers.user.datetime.date') as mock_date:
            mock_date.today.return_value = date(2018, 5, 15)
            mock_date.side_effect = lambda *args, **kw: date(*args, **kw)

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
        from datetime import date
        with mock.patch('SoftLayer.managers.user.datetime.date') as mock_date:
            mock_date.today.return_value = date(2018, 5, 15)
            mock_date.side_effect = lambda *args, **kw: date(*args, **kw)

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
            {"keyName": "TEST_3"},
            {"keyName": "TEST_4"}
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
        result = self.manager.format_permission_object(['ALL'])
        service_name = 'SoftLayer_User_Customer_CustomerPermission_Permission'
        expected = [
            {'key': 'T_2', 'keyName': 'TEST', 'name': 'A Testing Permission'},
            {'key': 'T_3', 'keyName': 'TEST_3', 'name': 'A Testing Permission 3'},
            {'key': 'T_4', 'keyName': 'TEST_4', 'name': 'A Testing Permission 4'},
            {'key': 'T_1', 'keyName': 'TICKET_VIEW', 'name': 'View Tickets'}
        ]
        self.assert_called_with(service_name, 'getAllObjects')
        self.assertEqual(expected, result)
