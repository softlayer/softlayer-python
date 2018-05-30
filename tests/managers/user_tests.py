"""
    SoftLayer.tests.managers.user_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import mock
import SoftLayer
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
