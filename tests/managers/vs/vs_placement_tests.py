"""
    SoftLayer.tests.managers.vs.vs_placement_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.

"""
from unittest import mock as mock

from SoftLayer.managers.vs_placement import PlacementManager
from SoftLayer import testing


class VSPlacementManagerTests(testing.TestCase):

    def set_up(self):
        self.manager = PlacementManager(self.client)

    def test_list(self):
        self.manager.list()
        self.assert_called_with('SoftLayer_Account', 'getPlacementGroups', mask=mock.ANY)

    def test_list_mask(self):
        mask = "mask[id]"
        self.manager.list(mask)
        self.assert_called_with('SoftLayer_Account', 'getPlacementGroups', mask=mask)

    def test_create(self):
        placement_object = {
            'backendRouter': 1234,
            'name': 'myName',
            'ruleId': 1
        }
        self.manager.create(placement_object)
        self.assert_called_with('SoftLayer_Virtual_PlacementGroup', 'createObject', args=(placement_object,))

    def test_get_object(self):
        self.manager.get_object(1234)
        self.assert_called_with('SoftLayer_Virtual_PlacementGroup', 'getObject', identifier=1234, mask=mock.ANY)

    def test_get_object_with_mask(self):
        mask = "mask[id]"
        self.manager.get_object(1234, mask)
        self.assert_called_with('SoftLayer_Virtual_PlacementGroup', 'getObject', identifier=1234, mask=mask)

    def test_delete(self):
        self.manager.delete(1234)
        self.assert_called_with('SoftLayer_Virtual_PlacementGroup', 'deleteObject', identifier=1234)

    def test_get_id_from_name(self):
        self.manager._get_id_from_name('test')
        _filter = {
            'placementGroups': {
                'name': {'operation': 'test'}
            }
        }
        self.assert_called_with('SoftLayer_Account', 'getPlacementGroups', filter=_filter, mask="mask[id, name]")

    def test_get_rule_id_from_name(self):
        result = self.manager.get_rule_id_from_name('SPREAD')
        self.assertEqual(result[0], 1)
        result = self.manager.get_rule_id_from_name('SpReAd')
        self.assertEqual(result[0], 1)

    def test_get_rule_id_from_name_failure(self):
        result = self.manager.get_rule_id_from_name('SPREAD1')
        self.assertEqual(result, [])

    def test_router_search(self):
        result = self.manager.get_backend_router_id_from_hostname('bcr01a.ams01')
        self.assertEqual(result[0], 117917)
        result = self.manager.get_backend_router_id_from_hostname('bcr01A.AMS01')
        self.assertEqual(result[0], 117917)

    def test_router_search_failure(self):
        result = self.manager.get_backend_router_id_from_hostname('1234.ams01')
        self.assertEqual(result, [])
