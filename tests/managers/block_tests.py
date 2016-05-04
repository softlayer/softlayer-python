"""
    SoftLayer.tests.managers.block_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""

import SoftLayer
from SoftLayer import fixtures
from SoftLayer import testing


class BlockTests(testing.TestCase):
    def set_up(self):
        self.block = SoftLayer.BlockStorageManager(self.client)

    def test_cancel_block_volume_immediately(self):
        self.block.cancel_block_volume(123, immediate=True)

        self.assert_called_with('SoftLayer_Billing_Item', 'cancelItem',
                                args=(True, True, 'No longer needed'),
                                identifier=449)

    def test_get_block_volume_details(self):
        result = self.block.get_block_volume_details(100)

        self.assertEqual(fixtures.SoftLayer_Network_Storage.getObject,
                         result)
        self.assert_called_with('SoftLayer_Network_Storage', 'getObject',
                                identifier=100)

    def test_list_block_volumes(self):
        result = self.block.list_block_volumes()

        self.assertEqual(fixtures.SoftLayer_Account.getIscsiNetworkStorage,
                         result)
        self.assert_called_with('SoftLayer_Account', 'getIscsiNetworkStorage')

    def test_get_block_volume_access_list(self):
        result = self.block.get_block_volume_access_list(100)

        self.assertEqual(fixtures.SoftLayer_Network_Storage.getObject,
                         result)
        self.assert_called_with('SoftLayer_Network_Storage', 'getObject',
                                identifier=100)

    def test_get_block_volume_snapshot_list(self):
        result = self.block.get_block_volume_snapshot_list(100)

        self.assertEqual(fixtures.SoftLayer_Network_Storage.getSnapshots,
                         result)
        self.assert_called_with('SoftLayer_Network_Storage', 'getSnapshots',
                                identifier=100)

    def test_delete_snapshot(self):
        result = self.block.delete_snapshot(100)

        self.assertEqual(fixtures.SoftLayer_Network_Storage.deleteObject,
                         result)
        self.assert_called_with('SoftLayer_Network_Storage', 'deleteObject',
                                identifier=100)

    def test_order_block_volume_no_package(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = []

        self.assertRaises(
            ValueError,
            self.block.order_block_volume,
            "performance_storage_iscsi", "dal05", 100, "LINUX", iops=100,
        )

    def test_order_block_volume_too_many_packages(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [{}, {}]

        self.assertRaises(
            ValueError,
            self.block.order_block_volume,
            "performance_storage_iscsi", "dal05", 100, "LINUX", iops=100,
        )

    def test_order_block_volume_performance(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [{
            'id': 1,
            'name': 'Performance',
            'items': [{
                'capacity': '1',
                'prices': [{
                    'id': 1,
                    'locationGroupId': '',
                    'categories': [{
                        'categoryCode': 'performance_storage_iscsi',
                    }],
                }],
            }, {
                'capacity': '100',
                'prices': [{
                    'id': 2,
                    'locationGroupId': '',
                    'categories': [{
                        'categoryCode': 'performance_storage_space',
                    }],
                }],
            }, {
                'capacity': '100',
                'prices': [{
                    'id': 3,
                    'locationGroupId': '',
                    'categories': [{
                        'categoryCode': 'performance_storage_iops',
                    }],
                    'capacityRestrictionMinimum': '100',
                    'capacityRestrictionMaximum': '100',
                }],
            }],
        }]

        result = self.block.order_block_volume(
            "performance_storage_iscsi", "dal05", 100, "LINUX", iops=100)

        self.assertEqual(
            result,
            {
                'orderDate': '2013-08-01 15:23:45',
                'orderId': 1234,
                'prices': [{
                    'hourlyRecurringFee': '2',
                    'id': 1,
                    'item': {'description': 'this is a thing', 'id': 1},
                    'laborFee': '2',
                    'oneTimeFee': '2',
                    'oneTimeFeeTax': '.1',
                    'quantity': 1,
                    'recurringFee': '2',
                    'recurringFeeTax': '.1',
                    'setupFee': '1'}],
                },
            )

    def test_order_block_volume_endurance(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [{
            'id': 1,
            'name': 'Performance',
            'items': [{
                'capacity': '1',
                'prices': [{
                    'id': 1,
                    'locationGroupId': '',
                    'categories': [{
                        'categoryCode': 'storage_block',
                    }],
                }],
            }, {
                'capacity': '1',
                'prices': [{
                    'id': 2,
                    'locationGroupId': '',
                    'categories': [{
                        'categoryCode': 'storage_service_enterprise',
                    }],
                }],
            }, {
                'capacity': '100',
                'prices': [{
                    'id': 3,
                    'locationGroupId': '',
                    'categories': [{
                        'categoryCode': 'performance_storage_space',
                    }],
                    'capacityRestrictionMinimum': '100',
                    'capacityRestrictionMaximum': '100',
                }],
            }, {
                'capacity': '100',
                'attributes': [{
                    'value': '100',
                }],
                'prices': [{
                    'id': 4,
                    'locationGroupId': '',
                    'categories': [{
                        'categoryCode': 'storage_tier_level',
                    }],
                }],
            }],
        }]

        result = self.block.order_block_volume(
            "storage_service_enterprise", "dal05", 100, "LINUX",
            tier_level=0.25)

        self.assertEqual(
            result,
            {
                'orderDate': '2013-08-01 15:23:45',
                'orderId': 1234,
                'prices': [{
                    'hourlyRecurringFee': '2',
                    'id': 1,
                    'item': {'description': 'this is a thing', 'id': 1},
                    'laborFee': '2',
                    'oneTimeFee': '2',
                    'oneTimeFeeTax': '.1',
                    'quantity': 1,
                    'recurringFee': '2',
                    'recurringFeeTax': '.1',
                    'setupFee': '1'}],
                },
            )
