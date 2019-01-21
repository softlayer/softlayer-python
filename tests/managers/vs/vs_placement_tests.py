"""
    SoftLayer.tests.managers.vs.vs_placement_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.

"""
import mock

import SoftLayer
from SoftLayer import fixtures
# from SoftLayer.fixtures import SoftLayer_Product_Package
from SoftLayer import testing
from SoftLayer.managers.vs_placement import PlacementManager


class VSPlacementManagerTests(testing.TestCase):

    def set_up(self):
        self.manager = PlacementManager(self.client)
        amock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')

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
        result = self.manager.get_object(1234)
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
            'placementGroups' : {
                'name': {'operation': 'test'}
            }
        }
        self.assert_called_with('SoftLayer_Account', 'getPlacementGroups', filter=_filter, mask="mask[id, name]")