"""
    SoftLayer.tests.CLI.modules.vs_placement_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
from unittest import mock as mock

from SoftLayer import testing


class VSPlacementTests(testing.TestCase):

    def test_create_options(self):
        result = self.run_command(['vs', 'placementgroup', 'create-options'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Virtual_PlacementGroup', 'getAvailableRouters')
        self.assert_called_with('SoftLayer_Virtual_PlacementGroup_Rule', 'getAllObjects')
        self.assertEqual([], self.calls('SoftLayer_Virtual_PlacementGroup', 'createObject'))

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_create_group(self, confirm_mock):
        confirm_mock.return_value = True
        result = self.run_command(['vs', 'placementgroup', 'create', '--name=test', '--backend_router=1', '--rule=2'])
        create_args = {
            'name': 'test',
            'backendRouterId': 1,
            'ruleId': 2
        }
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Virtual_PlacementGroup', 'createObject', args=(create_args,))
        self.assertEqual([], self.calls('SoftLayer_Virtual_PlacementGroup', 'getAvailableRouters'))

    def test_list_groups(self):
        result = self.run_command(['vs', 'placementgroup', 'list'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Account', 'getPlacementGroups')

    def test_detail_group_id(self):
        result = self.run_command(['vs', 'placementgroup', 'detail', '12345'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Virtual_PlacementGroup', 'getObject', identifier=12345)

    def test_detail_group_name(self):
        result = self.run_command(['vs', 'placementgroup', 'detail', 'test'])
        self.assert_no_fail(result)
        group_filter = {
            'placementGroups': {
                'name': {'operation': 'test'}
            }
        }
        self.assert_called_with('SoftLayer_Account', 'getPlacementGroups', filter=group_filter)
        self.assert_called_with('SoftLayer_Virtual_PlacementGroup', 'getObject', identifier=12345)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_delete_group_id(self, confirm_mock):
        confirm_mock.return_value = True
        result = self.run_command(['vs', 'placementgroup', 'delete', '12345'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Virtual_PlacementGroup', 'deleteObject', identifier=12345)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_delete_group_id_cancel(self, confirm_mock):
        confirm_mock.return_value = False
        result = self.run_command(['vs', 'placementgroup', 'delete', '12345'])
        self.assertEqual(result.exit_code, 2)
        self.assertEqual([], self.calls('SoftLayer_Virtual_PlacementGroup', 'deleteObject'))

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_delete_group_name(self, confirm_mock):
        confirm_mock.return_value = True
        result = self.run_command(['vs', 'placementgroup', 'delete', 'test'])
        group_filter = {
            'placementGroups': {
                'name': {'operation': 'test'}
            }
        }
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Account', 'getPlacementGroups', filter=group_filter)
        self.assert_called_with('SoftLayer_Virtual_PlacementGroup', 'deleteObject', identifier=12345)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_delete_group_purge(self, confirm_mock):
        confirm_mock.return_value = True
        result = self.run_command(['vs', 'placementgroup', 'delete', '1234', '--purge'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Virtual_PlacementGroup', 'getObject')
        self.assert_called_with('SoftLayer_Virtual_Guest', 'deleteObject', identifier=69131875)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_delete_group_purge_cancel(self, confirm_mock):
        confirm_mock.return_value = False
        result = self.run_command(['vs', 'placementgroup', 'delete', '1234', '--purge'])
        self.assertEqual(result.exit_code, 2)
        self.assertEqual([], self.calls('SoftLayer_Virtual_Guest', 'deleteObject'))

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_delete_group_purge_nothing(self, confirm_mock):
        group_mock = self.set_mock('SoftLayer_Virtual_PlacementGroup', 'getObject')
        group_mock.return_value = {
            "id": 1234,
            "name": "test-group",
            "guests": [],
        }
        confirm_mock.return_value = True
        result = self.run_command(['vs', 'placementgroup', 'delete', '1234', '--purge'])
        self.assertEqual(result.exit_code, 2)
        self.assert_called_with('SoftLayer_Virtual_PlacementGroup', 'getObject')
        self.assertEqual([], self.calls('SoftLayer_Virtual_Guest', 'deleteObject'))
