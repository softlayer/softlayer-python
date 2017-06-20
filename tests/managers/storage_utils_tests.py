"""
    SoftLayer.tests.managers.storage_utils_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""

import SoftLayer
from SoftLayer import exceptions
from SoftLayer import fixtures
from SoftLayer.managers import storage_utils
from SoftLayer import testing


class StorageUtilsTests(testing.TestCase):
    def set_up(self):
        self.block = SoftLayer.BlockStorageManager(self.client)
        self.file = SoftLayer.FileStorageManager(self.client)

    def test_find_saas_price_by_category_no_items_in_package(self):
        package = {
            'items': []}

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_saas_price_by_category,
            package, 'storage_as_a_service'
        )

        self.assertEqual(str(exception),
                         "Could not find price with the category, "
                         "storage_as_a_service")

    def test_find_saas_price_by_category_no_prices_in_items(self):
        package = {
            'items': [
                {'capacity': '0',
                 'prices': []}
            ]}

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_saas_price_by_category,
            package, 'storage_as_a_service'
        )

        self.assertEqual(str(exception),
                         "Could not find price with the category, "
                         "storage_as_a_service")

    def test_find_saas_price_by_category_empty_location_not_found(self):
        package = {
            'items': [
                {'capacity': '0',
                 'prices': [
                     {'id': 189433,
                      'categories': [
                          {'categoryCode': 'storage_as_a_service'}
                      ],
                      'locationGroupId': '77777777'}
                 ]}
            ]}

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_saas_price_by_category,
            package, 'storage_as_a_service'
        )

        self.assertEqual(str(exception),
                         "Could not find price with the category, "
                         "storage_as_a_service")

    def test_find_saas_price_by_category_category_not_found(self):
        package = {
            'items': [
                {'capacity': '0',
                 'prices': [
                     {'id': 189433,
                      'categories': [
                          {'categoryCode': 'invalid_category_noooo'}
                      ],
                      'locationGroupId': ''}
                 ]}
            ]}

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_saas_price_by_category,
            package, 'storage_as_a_service'
        )

        self.assertEqual(str(exception),
                         "Could not find price with the category, "
                         "storage_as_a_service")

    def test_find_saas_price_by_category(self):
        package = {
            'items': [
                {'capacity': '0',
                 'prices': [
                     {'id': 189433,
                      'categories': [
                          {'categoryCode': 'storage_as_a_service'}
                      ],
                      'locationGroupId': ''}
                 ]}
            ]}

        result = storage_utils.find_saas_price_by_category(
            package, 'storage_as_a_service')

        self.assertEqual({'id': 189433}, result)

    def test_find_saas_endurance_space_price_no_items_in_package(self):
        package = {
            'items': []}

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_saas_endurance_space_price,
            package, 8000, 0.25
        )

        self.assertEqual(str(exception),
                         "Could not find price for endurance storage space")

    def test_find_saas_endurance_space_price_no_matching_keyname(self):
        package = {
            'items': [
                {'capacity': '0',
                 'keyName': 'STORAGE_SPACE_FOR_2_IOPS_PER_GB'}
            ]}

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_saas_endurance_space_price,
            package, 8000, 0.25
        )

        self.assertEqual(str(exception),
                         "Could not find price for endurance storage space")

    def test_find_saas_endurance_space_price_no_capacity_maximum(self):
        package = {
            'items': [
                {'capacity': '0',
                 'capacityMinimum': '1',
                 'keyName': 'STORAGE_SPACE_FOR_0_25_IOPS_PER_GB'}
            ]}

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_saas_endurance_space_price,
            package, 8000, 0.25
        )

        self.assertEqual(str(exception),
                         "Could not find price for endurance storage space")

    def test_find_saas_endurance_space_price_no_capacity_minimum(self):
        package = {
            'items': [
                {'capacity': '0',
                 'capacityMaximum': '12000',
                 'keyName': 'STORAGE_SPACE_FOR_0_25_IOPS_PER_GB'}
            ]}

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_saas_endurance_space_price,
            package, 8000, 0.25
        )

        self.assertEqual(str(exception),
                         "Could not find price for endurance storage space")

    def test_find_saas_endurance_space_price_size_below_capacity(self):
        package = {
            'items': [
                {'capacity': '0',
                 'capacityMaximum': '12000',
                 'capacityMinimum': '1',
                 'keyName': 'STORAGE_SPACE_FOR_0_25_IOPS_PER_GB'}
            ]}

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_saas_endurance_space_price,
            package, 0, 0.25
        )

        self.assertEqual(str(exception),
                         "Could not find price for endurance storage space")

    def test_find_saas_endurance_space_price_size_above_capacity(self):
        package = {
            'items': [
                {'capacity': '0',
                 'capacityMaximum': '12000',
                 'capacityMinimum': '1',
                 'keyName': 'STORAGE_SPACE_FOR_0_25_IOPS_PER_GB'}
            ]}

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_saas_endurance_space_price,
            package, 12001, 0.25
        )

        self.assertEqual(str(exception),
                         "Could not find price for endurance storage space")

    def test_find_saas_endurance_space_price_no_prices_in_items(self):
        package = {
            'items': [
                {'capacity': '0',
                 'capacityMaximum': '12000',
                 'capacityMinimum': '1',
                 'keyName': 'STORAGE_SPACE_FOR_0_25_IOPS_PER_GB',
                 'prices': []}
            ]}

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_saas_endurance_space_price,
            package, 8000, 0.25
        )

        self.assertEqual(str(exception),
                         "Could not find price for endurance storage space")

    def test_find_saas_endurance_space_price_empty_location_not_found(self):
        package = {
            'items': [
                {'capacity': '0',
                 'capacityMaximum': '12000',
                 'capacityMinimum': '1',
                 'keyName': 'STORAGE_SPACE_FOR_0_25_IOPS_PER_GB',
                 'prices': [
                     {'id': 192103,
                      'categories': [
                          {'categoryCode': 'performance_storage_space'}
                      ],
                      'locationGroupId': '77777777'}
                 ]}
            ]}

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_saas_endurance_space_price,
            package, 8000, 0.25
        )

        self.assertEqual(str(exception),
                         "Could not find price for endurance storage space")

    def test_find_saas_endurance_space_price_category_not_found(self):
        package = {
            'items': [
                {'capacity': '0',
                 'capacityMaximum': '12000',
                 'capacityMinimum': '1',
                 'keyName': 'STORAGE_SPACE_FOR_0_25_IOPS_PER_GB',
                 'prices': [
                     {'id': 192103,
                      'categories': [
                          {'categoryCode': 'invalid_category_noooo'}
                      ],
                      'locationGroupId': ''}
                 ]}
            ]}

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_saas_endurance_space_price,
            package, 8000, 0.25
        )

        self.assertEqual(str(exception),
                         "Could not find price for endurance storage space")

    def test_find_saas_endurance_space_price(self):
        package = {
            'items': [
                {'capacity': '0',
                 'capacityMaximum': '12000',
                 'capacityMinimum': '1',
                 'keyName': 'STORAGE_SPACE_FOR_0_25_IOPS_PER_GB',
                 'prices': [
                     {'id': 192103,
                      'categories': [
                          {'categoryCode': 'performance_storage_space'}
                      ],
                      'locationGroupId': ''}
                 ]}
            ]}

        result = storage_utils.find_saas_endurance_space_price(
            package, 8000, 0.25)

        self.assertEqual({'id': 192103}, result)

    def test_find_saas_endurance_tier_price_no_items_in_package(self):
        package = {
            'items': []}

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_saas_endurance_tier_price,
            package, 2
        )

        self.assertEqual(str(exception),
                         "Could not find price for endurance tier level")

    def test_find_saas_endurance_tier_price_no_itemCategory(self):
        package = {
            'items': [
                {'capacity': '200'}
            ]}

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_saas_endurance_tier_price,
            package, 2
        )

        self.assertEqual(str(exception),
                         "Could not find price for endurance tier level")

    def test_find_saas_endurance_tier_price_no_itemCategory_code(self):
        package = {
            'items': [
                {'capacity': '200',
                 'itemCategory': {}}
            ]}

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_saas_endurance_tier_price,
            package, 2
        )

        self.assertEqual(str(exception),
                         "Could not find price for endurance tier level")

    def test_find_saas_endurance_tier_price_no_matching_itemCategory(self):
        package = {
            'items': [
                {'capacity': '200',
                 'itemCategory': {'categoryCode': 'invalid_category_noooo'}}
            ]}

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_saas_endurance_tier_price,
            package, 2
        )

        self.assertEqual(str(exception),
                         "Could not find price for endurance tier level")

    def test_find_saas_endurance_tier_price_no_matching_capacity(self):
        package = {
            'items': [
                {'capacity': '200',
                 'itemCategory': {'categoryCode': 'storage_tier_level'}}
            ]}

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_saas_endurance_tier_price,
            package, 10
        )

        self.assertEqual(str(exception),
                         "Could not find price for endurance tier level")

    def test_find_saas_endurance_tier_price_no_prices_in_items(self):
        package = {
            'items': [
                {'capacity': '200',
                 'itemCategory': {'categoryCode': 'storage_tier_level'},
                 'prices': []}
            ]}

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_saas_endurance_tier_price,
            package, 2
        )

        self.assertEqual(str(exception),
                         "Could not find price for endurance tier level")

    def test_find_saas_endurance_tier_price_empty_location_not_found(self):
        package = {
            'items': [
                {'capacity': '200',
                 'itemCategory': {'categoryCode': 'storage_tier_level'},
                 'prices': [
                     {'id': 193373,
                      'categories': [
                          {'categoryCode': 'storage_tier_level'}
                      ],
                      'locationGroupId': '77777777'}
                 ]}
            ]}

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_saas_endurance_tier_price,
            package, 2
        )

        self.assertEqual(str(exception),
                         "Could not find price for endurance tier level")

    def test_find_saas_endurance_tier_price_category_not_found(self):
        package = {
            'items': [
                {'capacity': '200',
                 'itemCategory': {'categoryCode': 'storage_tier_level'},
                 'prices': [
                     {'id': 193373,
                      'categories': [
                          {'categoryCode': 'invalid_category_noooo'}
                      ],
                      'locationGroupId': ''}
                 ]}
            ]}

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_saas_endurance_tier_price,
            package, 2
        )

        self.assertEqual(str(exception),
                         "Could not find price for endurance tier level")

    def test_find_saas_endurance_tier_price(self):
        package = {
            'items': [
                {'capacity': '200',
                 'itemCategory': {'categoryCode': 'storage_tier_level'},
                 'prices': [
                     {'id': 193373,
                      'categories': [
                          {'categoryCode': 'storage_tier_level'}
                      ],
                      'locationGroupId': ''}
                 ]}
            ]}

        result = storage_utils.find_saas_endurance_tier_price(
            package, 2)

        self.assertEqual({'id': 193373}, result)

    def test_find_saas_perform_space_price_no_items_in_package(self):
        package = {
            'items': []}

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_saas_perform_space_price,
            package, 500
        )

        self.assertEqual(str(exception),
                         "Could not find price for performance storage space")

    def test_find_saas_perform_space_price_no_itemCategory(self):
        package = {
            'items': [
                {'capacity': '0'}
            ]}

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_saas_perform_space_price,
            package, 500
        )

        self.assertEqual(str(exception),
                         "Could not find price for performance storage space")

    def test_find_saas_perform_space_price_no_itemCategory_code(self):
        package = {
            'items': [
                {'capacity': '0',
                 'itemCategory': {}}
            ]}

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_saas_perform_space_price,
            package, 500
        )

        self.assertEqual(str(exception),
                         "Could not find price for performance storage space")

    def test_find_saas_perform_space_price_no_matching_itemCategory(self):
        package = {
            'items': [
                {'capacity': '0',
                 'itemCategory': {'categoryCode': 'invalid_category_noooo'}}
            ]}

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_saas_perform_space_price,
            package, 500
        )

        self.assertEqual(str(exception),
                         "Could not find price for performance storage space")

    def test_find_saas_perform_space_price_no_capacity_maximum(self):
        package = {
            'items': [
                {'capacity': '0',
                 'capacityMinimum': '500',
                 'itemCategory': {'categoryCode': 'performance_storage_space'},
                 'keyName': '500_999_GBS'}
            ]}

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_saas_perform_space_price,
            package, 500
        )

        self.assertEqual(str(exception),
                         "Could not find price for performance storage space")

    def test_find_saas_perform_space_price_no_capacity_minimum(self):
        package = {
            'items': [
                {'capacity': '0',
                 'capacityMaximum': '999',
                 'itemCategory': {'categoryCode': 'performance_storage_space'},
                 'keyName': '500_999_GBS'}
            ]}

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_saas_perform_space_price,
            package, 500
        )

        self.assertEqual(str(exception),
                         "Could not find price for performance storage space")

    def test_find_saas_perform_space_price_size_below_capacity(self):
        package = {
            'items': [
                {'capacity': '0',
                 'capacityMaximum': '999',
                 'capacityMinimum': '500',
                 'itemCategory': {'categoryCode': 'performance_storage_space'},
                 'keyName': '500_999_GBS'}
            ]}

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_saas_perform_space_price,
            package, 499
        )

        self.assertEqual(str(exception),
                         "Could not find price for performance storage space")

    def test_find_saas_perform_space_price_size_above_capacity(self):
        package = {
            'items': [
                {'capacity': '0',
                 'capacityMaximum': '999',
                 'capacityMinimum': '500',
                 'itemCategory': {'categoryCode': 'performance_storage_space'},
                 'keyName': '500_999_GBS'}
            ]}

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_saas_perform_space_price,
            package, 1000
        )

        self.assertEqual(str(exception),
                         "Could not find price for performance storage space")

    def test_find_saas_perform_space_price_no_matching_keyname(self):
        package = {
            'items': [
                {'capacity': '0',
                 'capacityMaximum': '999',
                 'capacityMinimum': '500',
                 'itemCategory': {'categoryCode': 'performance_storage_space'},
                 'keyName': 'NOT_THE_CORRECT_KEYNAME'}
            ]}

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_saas_perform_space_price,
            package, 500
        )

        self.assertEqual(str(exception),
                         "Could not find price for performance storage space")

    def test_find_saas_perform_space_price_no_prices_in_items(self):
        package = {
            'items': [
                {'capacity': '0',
                 'capacityMaximum': '999',
                 'capacityMinimum': '500',
                 'itemCategory': {'categoryCode': 'performance_storage_space'},
                 'keyName': '500_999_GBS',
                 'prices': []}
            ]}

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_saas_perform_space_price,
            package, 500
        )

        self.assertEqual(str(exception),
                         "Could not find price for performance storage space")

    def test_find_saas_perform_space_price_empty_location_not_found(self):
        package = {
            'items': [
                {'capacity': '0',
                 'capacityMaximum': '999',
                 'capacityMinimum': '500',
                 'itemCategory': {'categoryCode': 'performance_storage_space'},
                 'keyName': '500_999_GBS',
                 'prices': [
                     {'id': 189993,
                      'categories': [
                          {'categoryCode': 'performance_storage_space'}
                      ],
                      'locationGroupId': '77777777'}
                 ]}
            ]}

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_saas_perform_space_price,
            package, 500
        )

        self.assertEqual(str(exception),
                         "Could not find price for performance storage space")

    def test_find_saas_perform_space_price_category_not_found(self):
        package = {
            'items': [
                {'capacity': '0',
                 'capacityMaximum': '999',
                 'capacityMinimum': '500',
                 'itemCategory': {'categoryCode': 'performance_storage_space'},
                 'keyName': '500_999_GBS',
                 'prices': [
                     {'id': 189993,
                      'categories': [
                          {'categoryCode': 'invalid_category_noooo'}
                      ],
                      'locationGroupId': ''}
                 ]}
            ]}

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_saas_perform_space_price,
            package, 500
        )

        self.assertEqual(str(exception),
                         "Could not find price for performance storage space")

    def test_find_saas_perform_space_price(self):
        package = {
            'items': [
                {'capacity': '0',
                 'capacityMaximum': '999',
                 'capacityMinimum': '500',
                 'itemCategory': {'categoryCode': 'performance_storage_space'},
                 'keyName': '500_999_GBS',
                 'prices': [
                     {'id': 189993,
                      'categories': [
                          {'categoryCode': 'performance_storage_space'}
                      ],
                      'locationGroupId': ''}
                 ]}
            ]}

        result = storage_utils.find_saas_perform_space_price(
            package, 500)

        self.assertEqual({'id': 189993}, result)

    def test_find_saas_perform_iops_price_no_items_in_package(self):
        package = {
            'items': []}

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_saas_perform_iops_price,
            package, 500, 1700
        )

        self.assertEqual(str(exception),
                         "Could not find price for iops for the given volume")

    def test_find_saas_perform_iops_price_no_itemCategory(self):
        package = {
            'items': [
                {'capacity': '0'}
            ]}

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_saas_perform_iops_price,
            package, 500, 1700
        )

        self.assertEqual(str(exception),
                         "Could not find price for iops for the given volume")

    def test_find_saas_perform_iops_price_no_itemCategory_code(self):
        package = {
            'items': [
                {'capacity': '0',
                 'itemCategory': {}}
            ]}

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_saas_perform_iops_price,
            package, 500, 1700
        )

        self.assertEqual(str(exception),
                         "Could not find price for iops for the given volume")

    def test_find_saas_perform_iops_price_no_matching_itemCategory(self):
        package = {
            'items': [
                {'capacity': '0',
                 'itemCategory': {'categoryCode': 'invalid_category_noooo'}}
            ]}

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_saas_perform_iops_price,
            package, 500, 1700
        )

        self.assertEqual(str(exception),
                         "Could not find price for iops for the given volume")

    def test_find_saas_perform_iops_price_no_capacity_maximum(self):
        package = {
            'items': [
                {'capacity': '0',
                 'capacityMinimum': '100',
                 'itemCategory': {'categoryCode': 'performance_storage_iops'}}
            ]}

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_saas_perform_iops_price,
            package, 500, 1700
        )

        self.assertEqual(str(exception),
                         "Could not find price for iops for the given volume")

    def test_find_saas_perform_iops_price_no_capacity_minimum(self):
        package = {
            'items': [
                {'capacity': '0',
                 'capacityMaximum': '10000',
                 'itemCategory': {'categoryCode': 'performance_storage_iops'}}
            ]}

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_saas_perform_iops_price,
            package, 500, 1700
        )

        self.assertEqual(str(exception),
                         "Could not find price for iops for the given volume")

    def test_find_saas_perform_iops_price_iops_below_capacity(self):
        package = {
            'items': [
                {'capacity': '0',
                 'capacityMaximum': '10000',
                 'capacityMinimum': '100',
                 'itemCategory': {'categoryCode': 'performance_storage_iops'}}
            ]}

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_saas_perform_iops_price,
            package, 500, 99
        )

        self.assertEqual(str(exception),
                         "Could not find price for iops for the given volume")

    def test_find_saas_perform_iops_price_iops_above_capacity(self):
        package = {
            'items': [
                {'capacity': '0',
                 'capacityMaximum': '10000',
                 'capacityMinimum': '100',
                 'itemCategory': {'categoryCode': 'performance_storage_iops'}}
            ]}

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_saas_perform_iops_price,
            package, 500, 10001
        )

        self.assertEqual(str(exception),
                         "Could not find price for iops for the given volume")

    def test_find_saas_perform_iops_price_no_prices_in_items(self):
        package = {
            'items': [
                {'capacity': '0',
                 'capacityMaximum': '10000',
                 'capacityMinimum': '100',
                 'itemCategory': {'categoryCode': 'performance_storage_iops'},
                 'prices': []}
            ]}

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_saas_perform_iops_price,
            package, 500, 1700
        )

        self.assertEqual(str(exception),
                         "Could not find price for iops for the given volume")

    def test_find_saas_perform_iops_price_empty_location_not_found(self):
        package = {
            'items': [
                {'capacity': '0',
                 'capacityMaximum': '10000',
                 'capacityMinimum': '100',
                 'itemCategory': {'categoryCode': 'performance_storage_iops'},
                 'prices': [
                     {'capacityRestrictionMaximum': '999',
                      'capacityRestrictionMinimum': '500',
                      'capacityRestrictionType': 'STORAGE_SPACE',
                      'categories': [
                          {'categoryCode': 'performance_storage_iops'}
                      ],
                      'id': 190053,
                      'locationGroupId': '77777777'}
                 ]}
            ]}

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_saas_perform_iops_price,
            package, 500, 1700
        )

        self.assertEqual(str(exception),
                         "Could not find price for iops for the given volume")

    def test_find_saas_perform_iops_price_category_not_found(self):
        package = {
            'items': [
                {'capacity': '0',
                 'capacityMaximum': '10000',
                 'capacityMinimum': '100',
                 'itemCategory': {'categoryCode': 'performance_storage_iops'},
                 'prices': [
                     {'capacityRestrictionMaximum': '999',
                      'capacityRestrictionMinimum': '500',
                      'capacityRestrictionType': 'STORAGE_SPACE',
                      'categories': [
                          {'categoryCode': 'invalid_category_noooo'}
                      ],
                      'id': 190053,
                      'locationGroupId': ''}
                 ]}
            ]}

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_saas_perform_iops_price,
            package, 500, 1700
        )

        self.assertEqual(str(exception),
                         "Could not find price for iops for the given volume")

    def test_find_saas_perform_iops_price_wrong_capacity_restriction(self):
        package = {
            'items': [
                {'capacity': '0',
                 'capacityMaximum': '10000',
                 'capacityMinimum': '100',
                 'itemCategory': {'categoryCode': 'performance_storage_iops'},
                 'prices': [
                     {'capacityRestrictionMaximum': '999',
                      'capacityRestrictionMinimum': '500',
                      'capacityRestrictionType': 'NOT_THE_CORRECT_TYPE',
                      'categories': [
                          {'categoryCode': 'performance_storage_iops'}
                      ],
                      'id': 190053,
                      'locationGroupId': ''}
                 ]}
            ]}

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_saas_perform_iops_price,
            package, 500, 1700
        )

        self.assertEqual(str(exception),
                         "Could not find price for iops for the given volume")

    def test_find_saas_perform_iops_price_size_below_capacity(self):
        package = {
            'items': [
                {'capacity': '0',
                 'capacityMaximum': '10000',
                 'capacityMinimum': '100',
                 'itemCategory': {'categoryCode': 'performance_storage_iops'},
                 'prices': [
                     {'capacityRestrictionMaximum': '999',
                      'capacityRestrictionMinimum': '500',
                      'capacityRestrictionType': 'STORAGE_SPACE',
                      'categories': [
                          {'categoryCode': 'performance_storage_iops'}
                      ],
                      'id': 190053,
                      'locationGroupId': ''}
                 ]}
            ]}

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_saas_perform_iops_price,
            package, 499, 1700
        )

        self.assertEqual(str(exception),
                         "Could not find price for iops for the given volume")

    def test_find_saas_perform_iops_price_size_above_capacity(self):
        package = {
            'items': [
                {'capacity': '0',
                 'capacityMaximum': '10000',
                 'capacityMinimum': '100',
                 'itemCategory': {'categoryCode': 'performance_storage_iops'},
                 'prices': [
                     {'capacityRestrictionMaximum': '999',
                      'capacityRestrictionMinimum': '500',
                      'capacityRestrictionType': 'STORAGE_SPACE',
                      'categories': [
                          {'categoryCode': 'performance_storage_iops'}
                      ],
                      'id': 190053,
                      'locationGroupId': ''}
                 ]}
            ]}

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_saas_perform_iops_price,
            package, 1000, 1700
        )

        self.assertEqual(str(exception),
                         "Could not find price for iops for the given volume")

    def test_find_saas_perform_iops_price(self):
        package = {
            'items': [
                {'capacity': '0',
                 'capacityMaximum': '10000',
                 'capacityMinimum': '100',
                 'itemCategory': {'categoryCode': 'performance_storage_iops'},
                 'prices': [
                     {'capacityRestrictionMaximum': '999',
                      'capacityRestrictionMinimum': '500',
                      'capacityRestrictionType': 'STORAGE_SPACE',
                      'categories': [
                          {'categoryCode': 'performance_storage_iops'}
                      ],
                      'id': 190053,
                      'locationGroupId': ''}
                 ]}
            ]}

        result = storage_utils.find_saas_perform_iops_price(
            package, 500, 1700)

        self.assertEqual({'id': 190053}, result)

    def test_find_saas_snapshot_space_price_no_items_in_package(self):
        package = {
            'items': []}

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_saas_snapshot_space_price,
            package, 10, iops=2100
        )

        self.assertEqual(str(exception),
                         "Could not find price for snapshot space")

    def test_find_saas_snapshot_space_price_no_matching_capacity(self):
        package = {
            'items': [
                {'capacity': '-1'}
            ]}

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_saas_snapshot_space_price,
            package, 10, iops=2100
        )

        self.assertEqual(str(exception),
                         "Could not find price for snapshot space")

    def test_find_saas_snapshot_space_price_no_prices_in_items(self):
        package = {
            'items': [
                {'capacity': '10',
                 'prices': []}
            ]}

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_saas_snapshot_space_price,
            package, 10, iops=2100
        )

        self.assertEqual(str(exception),
                         "Could not find price for snapshot space")

    def test_find_saas_snapshot_space_price_empty_location_not_found(self):
        package = {
            'items': [
                {'capacity': '10',
                 'prices': [
                     {'capacityRestrictionMaximum': '48000',
                      'capacityRestrictionMinimum': '100',
                      'capacityRestrictionType': 'IOPS',
                      'categories': [
                          {'categoryCode': 'storage_snapshot_space'}
                      ],
                      'id': 191193,
                      'locationGroupId': '77777777'}
                 ]}
            ]}

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_saas_snapshot_space_price,
            package, 10, iops=2100
        )

        self.assertEqual(str(exception),
                         "Could not find price for snapshot space")

    def test_find_saas_snapshot_space_price_wrong_capacity_restriction(self):
        package = {
            'items': [
                {'capacity': '10',
                 'prices': [
                     {'capacityRestrictionMaximum': '48000',
                      'capacityRestrictionMinimum': '100',
                      'capacityRestrictionType': 'NOT_THE_CORRECT_CATEGORY',
                      'categories': [
                          {'categoryCode': 'storage_snapshot_space'}
                      ],
                      'id': 191193,
                      'locationGroupId': ''}
                 ]}
            ]}

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_saas_snapshot_space_price,
            package, 10, iops=2100
        )

        self.assertEqual(str(exception),
                         "Could not find price for snapshot space")

    def test_find_saas_snapshot_space_price_target_value_below_capacity(self):
        package = {
            'items': [
                {'capacity': '10',
                 'prices': [
                     {'capacityRestrictionMaximum': '48000',
                      'capacityRestrictionMinimum': '100',
                      'capacityRestrictionType': 'IOPS',
                      'categories': [
                          {'categoryCode': 'storage_snapshot_space'}
                      ],
                      'id': 191193,
                      'locationGroupId': ''}
                 ]}
            ]}

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_saas_snapshot_space_price,
            package, 10, iops=99
        )

        self.assertEqual(str(exception),
                         "Could not find price for snapshot space")

    def test_find_saas_snapshot_space_price_target_value_above_capacity(self):
        package = {
            'items': [
                {'capacity': '10',
                 'prices': [
                     {'capacityRestrictionMaximum': '48000',
                      'capacityRestrictionMinimum': '100',
                      'capacityRestrictionType': 'IOPS',
                      'categories': [
                          {'categoryCode': 'storage_snapshot_space'}
                      ],
                      'id': 191193,
                      'locationGroupId': ''}
                 ]}
            ]}

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_saas_snapshot_space_price,
            package, 10, iops=48001
        )

        self.assertEqual(str(exception),
                         "Could not find price for snapshot space")

    def test_find_saas_snapshot_space_price_category_not_found(self):
        package = {
            'items': [
                {'capacity': '10',
                 'prices': [
                     {'capacityRestrictionMaximum': '48000',
                      'capacityRestrictionMinimum': '100',
                      'capacityRestrictionType': 'IOPS',
                      'categories': [
                          {'categoryCode': 'invalid_category_noooooooo'}
                      ],
                      'id': 191193,
                      'locationGroupId': ''}
                 ]}
            ]}

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_saas_snapshot_space_price,
            package, 10, iops=2100
        )

        self.assertEqual(str(exception),
                         "Could not find price for snapshot space")

    def test_find_saas_snapshot_space_price_with_iops(self):
        package = {
            'items': [
                {'capacity': '10',
                 'prices': [
                     {'capacityRestrictionMaximum': '48000',
                      'capacityRestrictionMinimum': '100',
                      'capacityRestrictionType': 'IOPS',
                      'categories': [
                          {'categoryCode': 'storage_snapshot_space'}
                      ],
                      'id': 191193,
                      'locationGroupId': ''}
                 ]}
            ]}

        result = storage_utils.find_saas_snapshot_space_price(
            package, 10, iops=2100)

        self.assertEqual({'id': 191193}, result)

    def test_find_saas_snapshot_space_price_with_tier_level(self):
        package = {
            'items': [
                {'capacity': '10',
                 'prices': [
                     {'capacityRestrictionMaximum': '200',
                      'capacityRestrictionMinimum': '200',
                      'capacityRestrictionType': 'STORAGE_TIER_LEVEL',
                      'categories': [
                          {'categoryCode': 'storage_snapshot_space'}
                      ],
                      'id': 193613,
                      'locationGroupId': ''}
                 ]}
            ]}

        result = storage_utils.find_saas_snapshot_space_price(
            package, 10, tier_level=2)

        self.assertEqual({'id': 193613}, result)

    def test_prep_duplicate_order_origin_volume_cancelled(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [fixtures.SoftLayer_Product_Package.SAAS_PACKAGE]

        mock_volume = fixtures.SoftLayer_Network_Storage.DUPLICATABLE_VOLUME
        prev_billing_item = mock_volume['billingItem']
        del mock_volume['billingItem']

        exception = self.assertRaises(
            exceptions.SoftLayerError,
            storage_utils.prepare_duplicate_order_object,
            self.block, mock_volume, None, None, None, None, 'block'
        )

        self.assertEqual(str(exception),
                         "The origin volume has been cancelled; "
                         "unable to order duplicate volume")

        mock_volume['billingItem'] = prev_billing_item

    def test_prep_duplicate_order_origin_snapshot_capacity_not_found(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [fixtures.SoftLayer_Product_Package.SAAS_PACKAGE]

        mock_volume = fixtures.SoftLayer_Network_Storage.DUPLICATABLE_VOLUME
        prev_snapshot_capacity_gb = mock_volume['snapshotCapacityGb']
        del mock_volume['snapshotCapacityGb']

        exception = self.assertRaises(
            exceptions.SoftLayerError,
            storage_utils.prepare_duplicate_order_object,
            self.block, mock_volume, None, None, None, None, 'block'
        )

        self.assertEqual(str(exception),
                         "Snapshot space not found for the origin volume. "
                         "Origin snapshot space is needed for duplication.")

        mock_volume['snapshotCapacityGb'] = prev_snapshot_capacity_gb

    def test_prep_duplicate_order_origin_volume_location_not_found(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [fixtures.SoftLayer_Product_Package.SAAS_PACKAGE]

        mock_volume = fixtures.SoftLayer_Network_Storage.DUPLICATABLE_VOLUME
        prev_location = mock_volume['billingItem']['location']
        del mock_volume['billingItem']['location']

        exception = self.assertRaises(
            exceptions.SoftLayerError,
            storage_utils.prepare_duplicate_order_object,
            self.block, mock_volume, None, None, None, None, 'block'
        )

        self.assertEqual(str(exception),
                         "Cannot find origin volume's location")

        mock_volume['billingItem']['location'] = prev_location

    def test_prep_duplicate_order_origin_volume_capacity_not_found(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [fixtures.SoftLayer_Product_Package.SAAS_PACKAGE]

        mock_volume = fixtures.SoftLayer_Network_Storage.DUPLICATABLE_VOLUME
        prev_capacity_gb = mock_volume['capacityGb']
        mock_volume['capacityGb'] = None

        exception = self.assertRaises(
            exceptions.SoftLayerError,
            storage_utils.prepare_duplicate_order_object,
            self.block, mock_volume, None, None, None, None, 'block'
        )

        self.assertEqual(str(exception), "Cannot find origin volume's size.")

        mock_volume['capacityGb'] = prev_capacity_gb

    def test_prep_duplicate_order_origin_originalVolumeSize_empty_block(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [fixtures.SoftLayer_Product_Package.SAAS_PACKAGE]

        mock_volume = fixtures.SoftLayer_Network_Storage.DUPLICATABLE_VOLUME
        prev_original_volume_size = mock_volume['originalVolumeSize']
        del mock_volume['originalVolumeSize']

        expected_object = {
            'complexType': 'SoftLayer_Container_Product_Order_'
                           'Network_Storage_AsAService',
            'packageId': 759,
            'prices': [
                {'id': 189433},
                {'id': 189443},
                {'id': 193433},
                {'id': 193373},
                {'id': 193613}
            ],
            'volumeSize': 500,
            'quantity': 1,
            'location': 449500,
            'duplicateOriginVolumeId': 102}

        result = storage_utils.prepare_duplicate_order_object(
            self.block, mock_volume, None, None, None, None, 'block')

        self.assertEqual(expected_object, result)

        mock_volume['originalVolumeSize'] = prev_original_volume_size

    def test_prep_duplicate_order_size_too_small(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [fixtures.SoftLayer_Product_Package.SAAS_PACKAGE]

        mock_volume = fixtures.SoftLayer_Network_Storage.DUPLICATABLE_VOLUME

        exception = self.assertRaises(
            exceptions.SoftLayerError,
            storage_utils.prepare_duplicate_order_object,
            self.block, mock_volume, None, None, 250, None, 'block'
        )

        self.assertEqual(str(exception),
                         "The requested duplicate volume size is too small. "
                         "Duplicate volumes must be at least as large as "
                         "their origin volumes.")

    def test_prep_duplicate_order_size_too_large_block(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [fixtures.SoftLayer_Product_Package.SAAS_PACKAGE]

        mock_volume = fixtures.SoftLayer_Network_Storage.DUPLICATABLE_VOLUME

        exception = self.assertRaises(
            exceptions.SoftLayerError,
            storage_utils.prepare_duplicate_order_object,
            self.block, mock_volume, None, None, 8000, None, 'block'
        )

        self.assertEqual(str(exception),
                         "The requested duplicate volume size is too large. "
                         "The maximum size for duplicate block volumes is 10 "
                         "times the size of the origin volume or, if the "
                         "origin volume was also a duplicate, 10 times the "
                         "size of the initial origin volume (i.e. the origin "
                         "volume from which the first duplicate was created "
                         "in the chain of duplicates). "
                         "Requested: 8000 GB. Base origin size: 500 GB.")

    def test_prep_duplicate_order_performance_origin_iops_not_found(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [fixtures.SoftLayer_Product_Package.SAAS_PACKAGE]

        mock_volume = fixtures.SoftLayer_Network_Storage.DUPLICATABLE_VOLUME
        prev_storage_type_keyname = mock_volume['storageType']['keyName']
        prev_provisioned_iops = mock_volume['provisionedIops']
        mock_volume['storageType']['keyName'] = 'PERFORMANCE_BLOCK_'\
                                                'STORAGE_REPLICANT'
        mock_volume['provisionedIops'] = None

        exception = self.assertRaises(
            exceptions.SoftLayerError,
            storage_utils.prepare_duplicate_order_object,
            self.block, mock_volume, None, None, None, None, 'block'
        )

        self.assertEqual(str(exception),
                         "Cannot find origin volume's provisioned IOPS")

        mock_volume['storageType']['keyName'] = prev_storage_type_keyname
        mock_volume['provisionedIops'] = prev_provisioned_iops

    def test_prep_duplicate_order_performance_iops_above_limit(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [fixtures.SoftLayer_Product_Package.SAAS_PACKAGE]

        mock_volume = fixtures.SoftLayer_Network_Storage.DUPLICATABLE_VOLUME
        prev_storage_type_keyname = mock_volume['storageType']['keyName']
        prev_provisioned_iops = mock_volume['provisionedIops']
        mock_volume['storageType']['keyName'] = 'PERFORMANCE_BLOCK_STORAGE'
        mock_volume['provisionedIops'] = '100'

        exception = self.assertRaises(
            exceptions.SoftLayerError,
            storage_utils.prepare_duplicate_order_object,
            self.block, mock_volume, 1000, None, 500, None, 'block'
        )

        self.assertEqual(str(exception),
                         "Origin volume performance is < 0.3 IOPS/GB, "
                         "duplicate volume performance must also be < 0.3 "
                         "IOPS/GB. 2.0 IOPS/GB (1000/500) requested.")

        mock_volume['storageType']['keyName'] = prev_storage_type_keyname
        mock_volume['provisionedIops'] = prev_provisioned_iops

    def test_prep_duplicate_order_performance_iops_below_limit(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [fixtures.SoftLayer_Product_Package.SAAS_PACKAGE]

        mock_volume = fixtures.SoftLayer_Network_Storage.DUPLICATABLE_VOLUME
        prev_storage_type_keyname = mock_volume['storageType']['keyName']
        mock_volume['storageType']['keyName'] = 'PERFORMANCE_BLOCK_STORAGE'

        exception = self.assertRaises(
            exceptions.SoftLayerError,
            storage_utils.prepare_duplicate_order_object,
            self.block, mock_volume, 200, None, 1000, None, 'block'
        )

        self.assertEqual(str(exception),
                         "Origin volume performance is >= 0.3 IOPS/GB, "
                         "duplicate volume performance must also be >= 0.3 "
                         "IOPS/GB. 0.2 IOPS/GB (200/1000) requested.")

        mock_volume['storageType']['keyName'] = prev_storage_type_keyname

    def test_prep_duplicate_order_performance_use_default_origin_values(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [fixtures.SoftLayer_Product_Package.SAAS_PACKAGE]

        mock_volume = fixtures.SoftLayer_Network_Storage.DUPLICATABLE_VOLUME
        prev_storage_type_keyname = mock_volume['storageType']['keyName']
        mock_volume['storageType']['keyName'] = 'PERFORMANCE_FILE_'\
                                                'STORAGE_REPLICANT'

        expected_object = {
            'complexType': 'SoftLayer_Container_Product_Order_'
                           'Network_Storage_AsAService',
            'packageId': 759,
            'prices': [
                {'id': 189433},
                {'id': 189453},
                {'id': 189993},
                {'id': 190053},
                {'id': 191193}
            ],
            'volumeSize': 500,
            'quantity': 1,
            'location': 449500,
            'duplicateOriginVolumeId': 102,
            'iops': 1000}

        result = storage_utils.prepare_duplicate_order_object(
            self.file, mock_volume, None, None, None, None, 'file')

        self.assertEqual(expected_object, result)

        mock_volume['storageType']['keyName'] = prev_storage_type_keyname

    def test_prep_duplicate_order_performance_block(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [fixtures.SoftLayer_Product_Package.SAAS_PACKAGE]

        mock_volume = fixtures.SoftLayer_Network_Storage.DUPLICATABLE_VOLUME
        prev_storage_type_keyname = mock_volume['storageType']['keyName']
        mock_volume['storageType']['keyName'] = 'PERFORMANCE_BLOCK_STORAGE'

        expected_object = {
            'complexType': 'SoftLayer_Container_Product_Order_'
                           'Network_Storage_AsAService',
            'packageId': 759,
            'prices': [
                {'id': 189433},
                {'id': 189443},
                {'id': 190113},
                {'id': 190173},
                {'id': 191193}
            ],
            'volumeSize': 1000,
            'quantity': 1,
            'location': 449500,
            'duplicateOriginVolumeId': 102,
            'iops': 2000}

        result = storage_utils.prepare_duplicate_order_object(
            self.block, mock_volume, 2000, None, 1000, 10, 'block')

        self.assertEqual(expected_object, result)

        mock_volume['storageType']['keyName'] = prev_storage_type_keyname

    def test_prep_duplicate_order_performance_file(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [fixtures.SoftLayer_Product_Package.SAAS_PACKAGE]

        mock_volume = fixtures.SoftLayer_Network_Storage.DUPLICATABLE_VOLUME
        prev_storage_type_keyname = mock_volume['storageType']['keyName']
        mock_volume['storageType']['keyName'] = 'PERFORMANCE_FILE_STORAGE'

        expected_object = {
            'complexType': 'SoftLayer_Container_Product_Order_'
                           'Network_Storage_AsAService',
            'packageId': 759,
            'prices': [
                {'id': 189433},
                {'id': 189453},
                {'id': 190113},
                {'id': 190173},
                {'id': 191193}
            ],
            'volumeSize': 1000,
            'quantity': 1,
            'location': 449500,
            'duplicateOriginVolumeId': 102,
            'iops': 2000}

        result = storage_utils.prepare_duplicate_order_object(
            self.file, mock_volume, 2000, None, 1000, 10, 'file')

        self.assertEqual(expected_object, result)

        mock_volume['storageType']['keyName'] = prev_storage_type_keyname

    def test_prep_duplicate_order_endurance_origin_tier_not_found(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [fixtures.SoftLayer_Product_Package.SAAS_PACKAGE]

        mock_volume = fixtures.SoftLayer_Network_Storage.DUPLICATABLE_VOLUME
        prev_tier_level = mock_volume['storageTierLevel']
        prev_storage_type_keyname = mock_volume['storageType']['keyName']
        mock_volume['storageTierLevel'] = 'NINJA_PENGUINS'
        mock_volume['storageType']['keyName'] = 'ENDURANCE_BLOCK_'\
                                                'STORAGE_REPLICANT'

        exception = self.assertRaises(
            exceptions.SoftLayerError,
            storage_utils.prepare_duplicate_order_object,
            self.block, mock_volume, None, None, None, None, 'block'
        )

        self.assertEqual(str(exception),
                         "Cannot find origin volume's tier level")

        mock_volume['storageTierLevel'] = prev_tier_level
        mock_volume['storageType']['keyName'] = prev_storage_type_keyname

    def test_prep_duplicate_order_endurance_tier_above_limit(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [fixtures.SoftLayer_Product_Package.SAAS_PACKAGE]

        mock_volume = fixtures.SoftLayer_Network_Storage.DUPLICATABLE_VOLUME
        prev_tier_level = mock_volume['storageTierLevel']
        mock_volume['storageTierLevel'] = 'LOW_INTENSITY_TIER'

        exception = self.assertRaises(
            exceptions.SoftLayerError,
            storage_utils.prepare_duplicate_order_object,
            self.block, mock_volume, None, 2, None, None, 'block'
        )

        self.assertEqual(str(exception),
                         "Origin volume performance tier is 0.25 IOPS/GB, "
                         "duplicate volume performance tier must also be 0.25 "
                         "IOPS/GB. 2 IOPS/GB requested.")

        mock_volume['storageTierLevel'] = prev_tier_level

    def test_prep_duplicate_order_endurance_tier_below_limit(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [fixtures.SoftLayer_Product_Package.SAAS_PACKAGE]

        mock_volume = fixtures.SoftLayer_Network_Storage.DUPLICATABLE_VOLUME

        exception = self.assertRaises(
            exceptions.SoftLayerError,
            storage_utils.prepare_duplicate_order_object,
            self.block, mock_volume, None, 0.25, None, None, 'block'
        )

        self.assertEqual(str(exception),
                         "Origin volume performance tier is above 0.25 "
                         "IOPS/GB, duplicate volume performance tier must "
                         "also be above 0.25 IOPS/GB. 0.25 IOPS/GB requested.")

    def test_prep_duplicate_order_endurance_use_default_origin_values(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [fixtures.SoftLayer_Product_Package.SAAS_PACKAGE]

        mock_volume = fixtures.SoftLayer_Network_Storage.DUPLICATABLE_VOLUME
        prev_storage_type_keyname = mock_volume['storageType']['keyName']
        mock_volume['storageType']['keyName'] = 'ENDURANCE_FILE_'\
                                                'STORAGE_REPLICANT'

        expected_object = {
            'complexType': 'SoftLayer_Container_Product_Order_'
                           'Network_Storage_AsAService',
            'packageId': 759,
            'prices': [
                {'id': 189433},
                {'id': 189453},
                {'id': 193433},
                {'id': 193373},
                {'id': 193613}
            ],
            'volumeSize': 500,
            'quantity': 1,
            'location': 449500,
            'duplicateOriginVolumeId': 102}

        result = storage_utils.prepare_duplicate_order_object(
            self.file, mock_volume, None, None, None, None, 'file')

        self.assertEqual(expected_object, result)

        mock_volume['storageType']['keyName'] = prev_storage_type_keyname

    def test_prep_duplicate_order_endurance_block(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [fixtures.SoftLayer_Product_Package.SAAS_PACKAGE]

        mock_volume = fixtures.SoftLayer_Network_Storage.DUPLICATABLE_VOLUME

        expected_object = {
            'complexType': 'SoftLayer_Container_Product_Order_'
                           'Network_Storage_AsAService',
            'packageId': 759,
            'prices': [
                {'id': 189433},
                {'id': 189443},
                {'id': 194763},
                {'id': 194703},
                {'id': 194943}
            ],
            'volumeSize': 1000,
            'quantity': 1,
            'location': 449500,
            'duplicateOriginVolumeId': 102}

        result = storage_utils.prepare_duplicate_order_object(
            self.block, mock_volume, None, 4.0, 1000, 10, 'block')

        self.assertEqual(expected_object, result)

    def test_prep_duplicate_order_endurance_file(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [fixtures.SoftLayer_Product_Package.SAAS_PACKAGE]

        mock_volume = fixtures.SoftLayer_Network_Storage.DUPLICATABLE_VOLUME
        prev_storage_type_keyname = mock_volume['storageType']['keyName']
        mock_volume['storageType']['keyName'] = 'ENDURANCE_FILE_STORAGE'

        expected_object = {
            'complexType': 'SoftLayer_Container_Product_Order_'
                           'Network_Storage_AsAService',
            'packageId': 759,
            'prices': [
                {'id': 189433},
                {'id': 189453},
                {'id': 194763},
                {'id': 194703},
                {'id': 194943}
            ],
            'volumeSize': 1000,
            'quantity': 1,
            'location': 449500,
            'duplicateOriginVolumeId': 102}

        result = storage_utils.prepare_duplicate_order_object(
            self.file, mock_volume, None, 4.0, 1000, 10, 'file')

        self.assertEqual(expected_object, result)

        mock_volume['storageType']['keyName'] = prev_storage_type_keyname

    def test_prep_duplicate_order_invalid_origin_storage_type(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [fixtures.SoftLayer_Product_Package.SAAS_PACKAGE]

        mock_volume = fixtures.SoftLayer_Network_Storage.DUPLICATABLE_VOLUME
        prev_storage_type_keyname = mock_volume['storageType']['keyName']
        mock_volume['storageType']['keyName'] = 'NINJA_CATS'

        exception = self.assertRaises(
            exceptions.SoftLayerError,
            storage_utils.prepare_duplicate_order_object,
            self.block, mock_volume, None, None, None, None, 'block'
        )

        self.assertEqual(str(exception),
                         "Origin volume does not have a valid storage type "
                         "(with an appropriate keyName to indicate the "
                         "volume is a PERFORMANCE or ENDURANCE volume)")

        mock_volume['storageType']['keyName'] = prev_storage_type_keyname
