"""
    SoftLayer.tests.managers.ordering_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import mock

import SoftLayer
from SoftLayer import exceptions
from SoftLayer import fixtures
from SoftLayer import testing


class ReservedCapacityTests(testing.TestCase):

    def set_up(self):
        self.reserved_capacity = SoftLayer.ReservedCapacityManager(self.client)

    def test_reserved_capacity_detail(self):
        result = self.reserved_capacity.detail(100)
        self.assert_called_with('SoftLayer_Virtual_ReservedCapacityGroup', 'getObject')
        self.assertEqual(result['id'], 100)

    def test_reserved_capacity_vs_instances(self):
        result = self.reserved_capacity.vs_instances(100)
        self.assert_called_with('SoftLayer_Virtual_ReservedCapacityGroup', 'getInstances')
        self.assertEqual(result[0]['guest']['id'], 1234)

    def test_reserved_capacity_edit(self):
        result = self.reserved_capacity.edit(100, 'test')
        self.assert_called_with('SoftLayer_Virtual_ReservedCapacityGroup', 'editObject')
        self.assertEqual(result, True)
