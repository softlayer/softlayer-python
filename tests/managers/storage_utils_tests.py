"""
    SoftLayer.tests.managers.storage_utils_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""

import copy
import SoftLayer
from SoftLayer import exceptions
from SoftLayer.fixtures import SoftLayer_Network_Storage
from SoftLayer.fixtures import SoftLayer_Product_Package
from SoftLayer.managers import storage_utils
from SoftLayer import testing


class StorageUtilsTests(testing.TestCase):
    def set_up(self):
        self.block = SoftLayer.BlockStorageManager(self.client)
        self.file = SoftLayer.FileStorageManager(self.client)

    # ---------------------------------------------------------------------
    # Tests for populate_host_templates()
    # ---------------------------------------------------------------------
    def test_populate_host_templates_no_ids_given(self):
        host_templates = []

        storage_utils.populate_host_templates(host_templates)

        self.assertEqual([], host_templates)

    def test_populate_host_templates_empty_arrays_given(self):
        host_templates = []

        storage_utils.populate_host_templates(
            host_templates,
            hardware_ids=[],
            virtual_guest_ids=[],
            ip_address_ids=[],
            subnet_ids=[]
        )

        self.assertEqual([], host_templates)

    def test_populate_host_templates(self):
        host_templates = []

        storage_utils.populate_host_templates(
            host_templates,
            hardware_ids=[1111],
            virtual_guest_ids=[2222],
            ip_address_ids=[3333],
            subnet_ids=[4444, 5555]
        )

        expected_result = [
            {'objectType': 'SoftLayer_Hardware', 'id': 1111},
            {'objectType': 'SoftLayer_Virtual_Guest', 'id': 2222},
            {'objectType': 'SoftLayer_Network_Subnet_IpAddress', 'id': 3333},
            {'objectType': 'SoftLayer_Network_Subnet', 'id': 4444},
            {'objectType': 'SoftLayer_Network_Subnet', 'id': 5555}
        ]

        self.assertEqual(expected_result, host_templates)

    # ---------------------------------------------------------------------
    # Tests for get_package()
    # ---------------------------------------------------------------------
    def test_get_package_no_packages_found(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = []

        exception = self.assertRaises(
            ValueError,
            storage_utils.get_package,
            self.block, 'storage_as_a_service'
        )

        self.assertEqual(
            "No packages were found for storage_as_a_service",
            str(exception)
        )

    def test_get_package_more_than_one_package_found(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [
            SoftLayer_Product_Package.SAAS_PACKAGE,
            SoftLayer_Product_Package.ENTERPRISE_PACKAGE
        ]

        exception = self.assertRaises(
            ValueError,
            storage_utils.get_package,
            self.block, 'storage_as_a_service'
        )

        self.assertEqual(
            "More than one package was found for storage_as_a_service",
            str(exception)
        )

    def test_get_package(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [SoftLayer_Product_Package.SAAS_PACKAGE]

        result = storage_utils.get_package(self.block, 'storage_as_a_service')

        self.assertEqual(
            SoftLayer_Product_Package.SAAS_PACKAGE,
            result
        )

        expected_filter = {
            'statusCode': {'operation': '_= ACTIVE'},
            'categories': {
                'categoryCode': {'operation': '_= storage_as_a_service'}
            }
        }

        self.assert_called_with(
            'SoftLayer_Product_Package',
            'getAllObjects',
            filter=expected_filter,
            mask='mask[id,name,items[prices[categories],attributes]]'
        )

    # ---------------------------------------------------------------------
    # Tests for get_location_id()
    # ---------------------------------------------------------------------
    def test_get_location_id_no_datacenters_in_collection(self):
        mock = self.set_mock('SoftLayer_Location_Datacenter', 'getDatacenters')
        mock.return_value = []

        exception = self.assertRaises(
            ValueError,
            storage_utils.get_location_id,
            self.block, 'dal09'
        )

        self.assertEqual("Invalid datacenter name specified.", str(exception))

    def test_get_location_id_no_matching_location_name(self):
        mock = self.set_mock('SoftLayer_Location_Datacenter', 'getDatacenters')
        mock.return_value = [
            {'id': 1414, 'name': 'hoth01'},
            {'id': 1417, 'name': 'hoth04'}
        ]

        exception = self.assertRaises(
            ValueError,
            storage_utils.get_location_id,
            self.block, 'dal09'
        )

        self.assertEqual("Invalid datacenter name specified.", str(exception))

    def test_get_location_id(self):
        mock = self.set_mock('SoftLayer_Location_Datacenter', 'getDatacenters')
        mock.return_value = [{'id': 29, 'name': 'dal09'}]

        result = storage_utils.get_location_id(self.block, 'dal09')

        self.assertEqual(29, result)

    # ---------------------------------------------------------------------
    # Tests for find_price_by_category()
    # ---------------------------------------------------------------------
    def test_find_price_by_category_no_items_in_package(self):
        package = {
            'items': []}

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_price_by_category,
            package, 'storage_as_a_service'
        )

        self.assertEqual(str(exception),
                         "Could not find price with the category, "
                         "storage_as_a_service")

    def test_find_price_by_category_no_prices_in_items(self):
        package = {
            'items': [
                {'capacity': '0',
                 'prices': []}
            ]}

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_price_by_category,
            package, 'storage_as_a_service'
        )

        self.assertEqual(str(exception),
                         "Could not find price with the category, "
                         "storage_as_a_service")

    def test_find_price_by_category_empty_location_not_found(self):
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
            storage_utils.find_price_by_category,
            package, 'storage_as_a_service'
        )

        self.assertEqual(str(exception),
                         "Could not find price with the category, "
                         "storage_as_a_service")

    def test_find_price_by_category_category_not_found(self):
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
            storage_utils.find_price_by_category,
            package, 'storage_as_a_service'
        )

        self.assertEqual(str(exception),
                         "Could not find price with the category, "
                         "storage_as_a_service")

    def test_find_price_by_category_empty(self):
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

        result = storage_utils.find_price_by_category(
            package, 'storage_as_a_service')

        self.assertEqual({'id': 189433}, result)

    def test_find_price_by_category_none(self):
        package = {
            'items': [
                {'capacity': '0',
                 'prices': [
                     {'id': 189433,
                      'categories': [
                          {'categoryCode': 'storage_as_a_service'}
                      ],
                      'locationGroupId': None}
                 ]}
            ]}

        result = storage_utils.find_price_by_category(
            package, 'storage_as_a_service')

        self.assertEqual({'id': 189433}, result)

    # ---------------------------------------------------------------------
    # Tests for find_ent_space_price()
    # ---------------------------------------------------------------------
    def test_find_ent_space_price_no_items_in_package(self):
        package = {
            'items': []
        }

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_ent_space_price,
            package, 'snapshot', 10, 2
        )

        self.assertEqual(
            "Could not find price for snapshot storage space",
            str(exception)
        )

    def test_find_ent_space_price_no_matching_capacity(self):
        package = {
            'items': [
                {'capacity': '-1'}
            ]
        }

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_ent_space_price,
            package, 'snapshot', 10, 2
        )

        self.assertEqual(
            "Could not find price for snapshot storage space",
            str(exception)
        )

    def test_find_ent_space_price_no_prices_in_items(self):
        package = {
            'items': [
                {
                    'capacity': '10',
                    'prices': []
                }
            ]
        }

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_ent_space_price,
            package, 'snapshot', 10, 2
        )

        self.assertEqual(
            "Could not find price for snapshot storage space",
            str(exception)
        )

    def test_find_ent_space_price_empty_location_not_found(self):
        package = {
            'items': [
                {
                    'capacity': '10',
                    'prices': [
                        {
                            'capacityRestrictionMaximum': '200',
                            'capacityRestrictionMinimum': '200',
                            'capacityRestrictionType': 'STORAGE_TIER_LEVEL',
                            'categories': [
                                {'categoryCode': 'storage_snapshot_space'}
                            ],
                            'id': 46160,
                            'locationGroupId': '77777777'
                        }
                    ]
                }
            ]
        }

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_ent_space_price,
            package, 'snapshot', 10, 2
        )

        self.assertEqual(
            "Could not find price for snapshot storage space",
            str(exception)
        )

    def test_find_ent_space_price_wrong_capacity_restriction(self):
        package = {
            'items': [
                {
                    'capacity': '10',
                    'prices': [
                        {
                            'capacityRestrictionMaximum': '200',
                            'capacityRestrictionMinimum': '200',
                            'capacityRestrictionType': 'WRONG_CATEGORY',
                            'categories': [
                                {'categoryCode': 'storage_snapshot_space'}
                            ],
                            'id': 46160,
                            'locationGroupId': ''
                        }
                    ]
                }
            ]
        }

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_ent_space_price,
            package, 'snapshot', 10, 2
        )

        self.assertEqual(
            "Could not find price for snapshot storage space",
            str(exception)
        )

    def test_find_ent_space_price_target_value_below_capacity(self):
        package = {
            'items': [
                {
                    'capacity': '10',
                    'prices': [
                        {
                            'capacityRestrictionMaximum': '200',
                            'capacityRestrictionMinimum': '200',
                            'capacityRestrictionType': 'STORAGE_TIER_LEVEL',
                            'categories': [
                                {'categoryCode': 'storage_snapshot_space'}
                            ],
                            'id': 46160,
                            'locationGroupId': ''
                        }
                    ]
                }
            ]
        }

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_ent_space_price,
            package, 'snapshot', 10, 0.25
        )

        self.assertEqual(
            "Could not find price for snapshot storage space",
            str(exception)
        )

    def test_find_ent_space_price_target_value_above_capacity(self):
        package = {
            'items': [
                {
                    'capacity': '10',
                    'prices': [
                        {
                            'capacityRestrictionMaximum': '200',
                            'capacityRestrictionMinimum': '200',
                            'capacityRestrictionType': 'STORAGE_TIER_LEVEL',
                            'categories': [
                                {'categoryCode': 'storage_snapshot_space'}
                            ],
                            'id': 46160,
                            'locationGroupId': ''
                        }
                    ]
                }
            ]
        }

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_ent_space_price,
            package, 'snapshot', 10, 4
        )

        self.assertEqual(
            "Could not find price for snapshot storage space",
            str(exception)
        )

    def test_find_ent_space_price_category_not_found(self):
        package = {
            'items': [
                {
                    'capacity': '10',
                    'prices': [
                        {
                            'capacityRestrictionMaximum': '200',
                            'capacityRestrictionMinimum': '200',
                            'capacityRestrictionType': 'STORAGE_TIER_LEVEL',
                            'categories': [
                                {'categoryCode': 'invalid_category_noooooooo'}
                            ],
                            'id': 46160,
                            'locationGroupId': ''
                        }
                    ]
                }
            ]
        }

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_ent_space_price,
            package, 'snapshot', 10, 2
        )

        self.assertEqual(
            "Could not find price for snapshot storage space",
            str(exception)
        )

    def test_find_ent_space_price_with_snapshot_category(self):
        package = {
            'items': [
                {
                    'capacity': '10',
                    'prices': [
                        {
                            'capacityRestrictionMaximum': '200',
                            'capacityRestrictionMinimum': '200',
                            'capacityRestrictionType': 'STORAGE_TIER_LEVEL',
                            'categories': [
                                {'categoryCode': 'storage_snapshot_space'}
                            ],
                            'id': 46160,
                            'locationGroupId': ''
                        }
                    ]
                }
            ]
        }

        result = storage_utils.find_ent_space_price(
            package, 'snapshot', 10, 2
        )

        self.assertEqual({'id': 46160}, result)

    def test_find_ent_space_price_with_replication_category(self):
        package = {
            'items': [
                {
                    'capacity': '20',
                    'prices': [
                        {
                            'capacityRestrictionMaximum': '200',
                            'capacityRestrictionMinimum': '200',
                            'capacityRestrictionType': 'STORAGE_TIER_LEVEL',
                            'categories': [
                                {'categoryCode':
                                    'performance_storage_replication'}
                            ],
                            'id': 46659,
                            'locationGroupId': ''
                        }
                    ]
                }
            ]
        }

        result = storage_utils.find_ent_space_price(
            package, 'replication', 20, 2
        )

        self.assertEqual({'id': 46659}, result)

    def test_find_ent_space_price_with_endurance_category(self):
        package = {
            'items': [
                {
                    'capacity': '1000',
                    'prices': [
                        {
                            'capacityRestrictionMaximum': '300',
                            'capacityRestrictionMinimum': '300',
                            'capacityRestrictionType': 'STORAGE_TIER_LEVEL',
                            'categories': [
                                {'categoryCode': 'performance_storage_space'}
                            ],
                            'id': 45318,
                            'locationGroupId': ''
                        }
                    ]
                }
            ]
        }

        result = storage_utils.find_ent_space_price(
            package, 'endurance', 1000, 4
        )

        self.assertEqual({'id': 45318}, result)

    # ---------------------------------------------------------------------
    # Tests for find_ent_endurance_tier_price()
    # ---------------------------------------------------------------------
    def test_find_ent_endurance_tier_price_no_items_in_package(self):
        package = {
            'items': []
        }

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_ent_endurance_tier_price,
            package, 2
        )

        self.assertEqual(
            "Could not find price for endurance tier level",
            str(exception)
        )

    def test_find_ent_endurance_tier_price_no_attributes_in_items(self):
        package = {
            'items': [
                {'attributes': []}
            ]
        }

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_ent_endurance_tier_price,
            package, 2
        )

        self.assertEqual(
            "Could not find price for endurance tier level",
            str(exception)
        )

    def test_find_ent_endurance_tier_price_no_matching_attribute_value(self):
        package = {
            'items': [
                {
                    'attributes': [
                        {'value': '-1'}
                    ]
                }
            ]
        }

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_ent_endurance_tier_price,
            package, 2
        )

        self.assertEqual(
            "Could not find price for endurance tier level",
            str(exception)
        )

    def test_find_ent_endurance_tier_price_no_prices_in_items(self):
        package = {
            'items': [
                {
                    'attributes': [
                        {'value': '200'}
                    ],
                    'prices': []
                }
            ]
        }

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_ent_endurance_tier_price,
            package, 2
        )

        self.assertEqual(
            "Could not find price for endurance tier level",
            str(exception)
        )

    def test_find_ent_endurance_tier_price_empty_location_not_found(self):
        package = {
            'items': [
                {
                    'attributes': [
                        {'value': '200'}
                    ],
                    'prices': [
                        {
                            'categories': [
                                {'categoryCode': 'storage_tier_level'}
                            ],
                            'id': 45078,
                            'locationGroupId': '77777777'
                        }
                    ]
                }
            ]
        }

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_ent_endurance_tier_price,
            package, 2
        )

        self.assertEqual(
            "Could not find price for endurance tier level",
            str(exception)
        )

    def test_find_ent_endurance_tier_price_category_not_found(self):
        package = {
            'items': [
                {
                    'attributes': [
                        {'value': '200'}
                    ],
                    'prices': [
                        {
                            'categories': [
                                {'categoryCode': 'invalid_category_noooo'}
                            ],
                            'id': 45078,
                            'locationGroupId': ''
                        }
                    ]
                }
            ]
        }

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_ent_endurance_tier_price,
            package, 2
        )

        self.assertEqual(
            "Could not find price for endurance tier level",
            str(exception)
        )

    def test_find_ent_endurance_tier_price(self):
        package = {
            'items': [
                {
                    'attributes': [
                        {'value': '200'}
                    ],
                    'prices': [
                        {
                            'categories': [
                                {'categoryCode': 'storage_tier_level'}
                            ],
                            'id': 45078,
                            'locationGroupId': ''
                        }
                    ]
                }
            ]
        }

        result = storage_utils.find_ent_endurance_tier_price(package, 2)

        self.assertEqual({'id': 45078}, result)

    # ---------------------------------------------------------------------
    # Tests for find_endurance_tier_iops_per_gb()
    # ---------------------------------------------------------------------
    def test_find_endurance_tier_iops_per_gb_value_is_025(self):
        volume = {'storageTierLevel': 'LOW_INTENSITY_TIER'}
        result = storage_utils.find_endurance_tier_iops_per_gb(volume)
        self.assertEqual(0.25, result)

    def test_find_endurance_tier_iops_per_gb_value_is_2(self):
        volume = {'storageTierLevel': 'READHEAVY_TIER'}
        result = storage_utils.find_endurance_tier_iops_per_gb(volume)
        self.assertEqual(2, result)

    def test_find_endurance_tier_iops_per_gb_value_is_4(self):
        volume = {'storageTierLevel': 'WRITEHEAVY_TIER'}
        result = storage_utils.find_endurance_tier_iops_per_gb(volume)
        self.assertEqual(4, result)

    def test_find_endurance_tier_iops_per_gb_value_is_10(self):
        volume = {'storageTierLevel': '10_IOPS_PER_GB'}
        result = storage_utils.find_endurance_tier_iops_per_gb(volume)
        self.assertEqual(10, result)

    def test_find_endurance_tier_iops_per_gb_value_not_found(self):
        volume = {'storageTierLevel': 'INVALID_TIER_OH_NOOOO'}

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_endurance_tier_iops_per_gb,
            volume
        )

        self.assertEqual(
            "Could not find tier IOPS per GB for this volume",
            str(exception)
        )

    # ---------------------------------------------------------------------
    # Tests for find_perf_space_price()
    # ---------------------------------------------------------------------
    def test_find_perf_space_price_no_items_in_package(self):
        package = {
            'items': []
        }

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_perf_space_price,
            package, 1000
        )

        self.assertEqual(
            "Could not find performance space price for this volume",
            str(exception)
        )

    def test_find_perf_space_price_no_matching_capacity(self):
        package = {
            'items': [
                {'capacity': '-1'}
            ]
        }

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_perf_space_price,
            package, 1000
        )

        self.assertEqual(
            "Could not find performance space price for this volume",
            str(exception)
        )

    def test_find_perf_space_price_no_prices_in_items(self):
        package = {
            'items': [
                {
                    'capacity': '1000',
                    'prices': []
                }
            ]
        }

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_perf_space_price,
            package, 1000
        )

        self.assertEqual(
            "Could not find performance space price for this volume",
            str(exception)
        )

    def test_find_perf_space_price_empty_location_not_found(self):
        package = {
            'items': [
                {
                    'capacity': '1000',
                    'prices': [
                        {
                            'categories': [
                                {'categoryCode': 'performance_storage_space'}
                            ],
                            'id': 40742,
                            'locationGroupId': '77777777'
                        }
                    ]
                }
            ]
        }

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_perf_space_price,
            package, 1000
        )

        self.assertEqual(
            "Could not find performance space price for this volume",
            str(exception)
        )

    def test_find_perf_space_price_category_not_found(self):
        package = {
            'items': [
                {
                    'capacity': '1000',
                    'prices': [
                        {
                            'categories': [
                                {'categoryCode': 'invalid_category_noooo'}
                            ],
                            'id': 40742,
                            'locationGroupId': ''
                        }
                    ]
                }
            ]
        }

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_perf_space_price,
            package, 1000
        )

        self.assertEqual(
            "Could not find performance space price for this volume",
            str(exception)
        )

    def test_find_perf_space_price(self):
        package = {
            'items': [
                {
                    'capacity': '1000',
                    'prices': [
                        {
                            'categories': [
                                {'categoryCode': 'performance_storage_space'}
                            ],
                            'id': 40742,
                            'locationGroupId': ''
                        }
                    ]
                }
            ]
        }

        result = storage_utils.find_perf_space_price(
            package, 1000
        )

        self.assertEqual({'id': 40742}, result)

    # ---------------------------------------------------------------------
    # Tests for find_perf_iops_price()
    # ---------------------------------------------------------------------
    def test_find_perf_iops_price_no_items_in_package(self):
        package = {
            'items': []
        }

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_perf_iops_price,
            package, 500, 800
        )

        self.assertEqual(
            "Could not find price for iops for the given volume",
            str(exception)
        )

    def test_find_perf_iops_price_no_matching_iops_value(self):
        package = {
            'items': [
                {'capacity': '-1'}
            ]
        }

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_perf_iops_price,
            package, 500, 800
        )

        self.assertEqual(
            "Could not find price for iops for the given volume",
            str(exception)
        )

    def test_find_perf_iops_price_no_prices_in_items(self):
        package = {
            'items': [
                {
                    'capacity': '800',
                    'keyName': '800_IOPS_4',
                    'prices': []
                }
            ]
        }

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_perf_iops_price,
            package, 500, 800
        )

        self.assertEqual(
            "Could not find price for iops for the given volume",
            str(exception)
        )

    def test_find_perf_iops_price_empty_location_not_found(self):
        package = {
            'items': [
                {
                    'capacity': '800',
                    'keyName': '800_IOPS_4',
                    'prices': [
                        {
                            'capacityRestrictionMaximum': '1000',
                            'capacityRestrictionMinimum': '100',
                            'capacityRestrictionType': 'STORAGE_SPACE',
                            'categories': [
                                {'categoryCode': 'performance_storage_iops'}
                            ],
                            'id': 41562,
                            'locationGroupId': '77777777'
                        }
                    ]
                }
            ]
        }

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_perf_iops_price,
            package, 500, 800
        )

        self.assertEqual(
            "Could not find price for iops for the given volume",
            str(exception)
        )

    def test_find_perf_iops_price_category_not_found(self):
        package = {
            'items': [
                {
                    'capacity': '800',
                    'keyName': '800_IOPS_4',
                    'prices': [
                        {
                            'capacityRestrictionMaximum': '1000',
                            'capacityRestrictionMinimum': '100',
                            'capacityRestrictionType': 'STORAGE_SPACE',
                            'categories': [
                                {'categoryCode': 'invalid_category_noooo'}
                            ],
                            'id': 41562,
                            'locationGroupId': ''
                        }
                    ]
                }
            ]
        }

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_perf_iops_price,
            package, 500, 800
        )

        self.assertEqual(
            "Could not find price for iops for the given volume",
            str(exception)
        )

    def test_find_perf_iops_price_wrong_capacity_restriction(self):
        package = {
            'items': [
                {
                    'capacity': '800',
                    'keyName': '800_IOPS_4',
                    'prices': [
                        {
                            'capacityRestrictionMaximum': '1000',
                            'capacityRestrictionMinimum': '100',
                            'capacityRestrictionType': 'WRONG_TYPE_WOAH',
                            'categories': [
                                {'categoryCode': 'performance_storage_iops'}
                            ],
                            'id': 41562,
                            'locationGroupId': ''
                        }
                    ]
                }
            ]
        }

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_perf_iops_price,
            package, 500, 800
        )

        self.assertEqual(
            "Could not find price for iops for the given volume",
            str(exception)
        )

    def test_find_perf_iops_price_volume_size_below_capacity(self):
        package = {
            'items': [
                {
                    'capacity': '800',
                    'keyName': '800_IOPS_4',
                    'prices': [
                        {
                            'capacityRestrictionMaximum': '1000',
                            'capacityRestrictionMinimum': '100',
                            'capacityRestrictionType': 'STORAGE_SPACE',
                            'categories': [
                                {'categoryCode': 'performance_storage_iops'}
                            ],
                            'id': 41562,
                            'locationGroupId': ''
                        }
                    ]
                }
            ]
        }

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_perf_iops_price,
            package, 80, 800
        )

        self.assertEqual(
            "Could not find price for iops for the given volume",
            str(exception)
        )

    def test_find_perf_iops_price_volume_size_above_capacity(self):
        package = {
            'items': [
                {
                    'capacity': '800',
                    'keyName': '800_IOPS_4',
                    'prices': [
                        {
                            'capacityRestrictionMaximum': '1000',
                            'capacityRestrictionMinimum': '100',
                            'capacityRestrictionType': 'STORAGE_SPACE',
                            'categories': [
                                {'categoryCode': 'performance_storage_iops'}
                            ],
                            'id': 41562,
                            'locationGroupId': ''
                        }
                    ]
                }
            ]
        }

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_perf_iops_price,
            package, 2000, 800
        )

        self.assertEqual(
            "Could not find price for iops for the given volume",
            str(exception)
        )

    def test_find_perf_iops_price(self):
        package = {
            'items': [
                {
                    'capacity': '800',
                    'keyName': '800_IOPS_4',
                    'prices': [
                        {
                            'capacityRestrictionMaximum': '1000',
                            'capacityRestrictionMinimum': '100',
                            'capacityRestrictionType': 'STORAGE_SPACE',
                            'categories': [
                                {'categoryCode': 'performance_storage_iops'}
                            ],
                            'id': 41562,
                            'locationGroupId': ''
                        }
                    ]
                }
            ]
        }

        result = storage_utils.find_perf_iops_price(
            package, 500, 800
        )

        self.assertEqual({'id': 41562}, result)

    # ---------------------------------------------------------------------
    # Tests for find_saas_endurance_space_price()
    # ---------------------------------------------------------------------
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

    # ---------------------------------------------------------------------
    # Tests for find_saas_endurance_tier_price()
    # ---------------------------------------------------------------------
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

    # ---------------------------------------------------------------------
    # Tests for find_saas_perform_space_price()
    # ---------------------------------------------------------------------
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

    # ---------------------------------------------------------------------
    # Tests for find_saas_perform_iops_price()
    # ---------------------------------------------------------------------
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

    # ---------------------------------------------------------------------
    # Tests for find_saas_snapshot_space_price()
    # ---------------------------------------------------------------------
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
            package, 10, tier=2)

        self.assertEqual({'id': 193613}, result)

    # ---------------------------------------------------------------------
    # Tests for find_saas_replication_price ()
    # ---------------------------------------------------------------------
    def test_find_saas_replication_price_no_items_in_package(self):
        package = {
            'items': []
        }

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_saas_replication_price,
            package, tier=2
        )

        self.assertEqual(
            "Could not find price for replicant volume",
            str(exception)
        )

    def test_find_saas_replication_price_no_matching_key_name(self):
        package = {
            'items': [
                {'keyName': 'THIS_IS_NOT_THE_ITEM_YOU_ARE_LOOKING_FOR'}
            ]
        }

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_saas_replication_price,
            package, tier=2
        )

        self.assertEqual(
            "Could not find price for replicant volume",
            str(exception)
        )

    def test_find_saas_replication_price_no_prices_in_items(self):
        package = {
            'items': [
                {
                    'keyName': 'REPLICATION_FOR_TIERBASED_PERFORMANCE',
                    'prices': []
                }
            ]
        }

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_saas_replication_price,
            package, tier=2
        )

        self.assertEqual(
            "Could not find price for replicant volume",
            str(exception)
        )

    def test_find_saas_replication_price_empty_location_not_found(self):
        package = {
            'items': [
                {
                    'keyName': 'REPLICATION_FOR_TIERBASED_PERFORMANCE',
                    'prices': [
                        {
                            'capacityRestrictionMaximum': '200',
                            'capacityRestrictionMinimum': '200',
                            'capacityRestrictionType': 'STORAGE_TIER_LEVEL',
                            'categories': [
                                {'categoryCode':
                                    'performance_storage_replication'}
                            ],
                            'id': 194693,
                            'locationGroupId': '77777777'
                        }
                    ]
                }
            ]
        }

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_saas_replication_price,
            package, tier=2
        )

        self.assertEqual(
            "Could not find price for replicant volume",
            str(exception)
        )

    def test_find_saas_replication_price_wrong_capacity_restriction(self):
        package = {
            'items': [
                {
                    'keyName': 'REPLICATION_FOR_TIERBASED_PERFORMANCE',
                    'prices': [
                        {
                            'capacityRestrictionMaximum': '200',
                            'capacityRestrictionMinimum': '200',
                            'capacityRestrictionType': 'WRONG_TYPE_WOAH',
                            'categories': [
                                {'categoryCode':
                                    'performance_storage_replication'}
                            ],
                            'id': 194693,
                            'locationGroupId': ''
                        }
                    ]
                }
            ]
        }

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_saas_replication_price,
            package, tier=2
        )

        self.assertEqual(
            "Could not find price for replicant volume",
            str(exception)
        )

    def test_find_saas_replication_price_target_value_below_capacity(self):
        package = {
            'items': [
                {
                    'keyName': 'REPLICATION_FOR_TIERBASED_PERFORMANCE',
                    'prices': [
                        {
                            'capacityRestrictionMaximum': '200',
                            'capacityRestrictionMinimum': '200',
                            'capacityRestrictionType': 'STORAGE_TIER_LEVEL',
                            'categories': [
                                {'categoryCode':
                                    'performance_storage_replication'}
                            ],
                            'id': 194693,
                            'locationGroupId': ''
                        }
                    ]
                }
            ]
        }

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_saas_replication_price,
            package, tier=0.25
        )

        self.assertEqual(
            "Could not find price for replicant volume",
            str(exception)
        )

    def test_find_saas_replication_price_target_value_above_capacity(self):
        package = {
            'items': [
                {
                    'keyName': 'REPLICATION_FOR_TIERBASED_PERFORMANCE',
                    'prices': [
                        {
                            'capacityRestrictionMaximum': '200',
                            'capacityRestrictionMinimum': '200',
                            'capacityRestrictionType': 'STORAGE_TIER_LEVEL',
                            'categories': [
                                {'categoryCode':
                                    'performance_storage_replication'}
                            ],
                            'id': 194693,
                            'locationGroupId': ''
                        }
                    ]
                }
            ]
        }

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_saas_replication_price,
            package, tier=4
        )

        self.assertEqual(
            "Could not find price for replicant volume",
            str(exception)
        )

    def test_find_saas_replication_price_category_not_found(self):
        package = {
            'items': [
                {
                    'keyName': 'REPLICATION_FOR_TIERBASED_PERFORMANCE',
                    'prices': [
                        {
                            'capacityRestrictionMaximum': '200',
                            'capacityRestrictionMinimum': '200',
                            'capacityRestrictionType': 'STORAGE_TIER_LEVEL',
                            'categories': [
                                {'categoryCode': 'invalid_category_oh_noooo'}
                            ],
                            'id': 194693,
                            'locationGroupId': ''
                        }
                    ]
                }
            ]
        }

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_saas_replication_price,
            package, tier=2
        )

        self.assertEqual(
            "Could not find price for replicant volume",
            str(exception)
        )

    def test_find_saas_replication_price_with_tier(self):
        package = {
            'items': [
                {
                    'keyName': 'REPLICATION_FOR_TIERBASED_PERFORMANCE',
                    'prices': [
                        {
                            'capacityRestrictionMaximum': '200',
                            'capacityRestrictionMinimum': '200',
                            'capacityRestrictionType': 'STORAGE_TIER_LEVEL',
                            'categories': [
                                {'categoryCode':
                                    'performance_storage_replication'}
                            ],
                            'id': 194693,
                            'locationGroupId': ''
                        }
                    ]
                }
            ]
        }

        result = storage_utils.find_saas_replication_price(
            package, tier=2
        )

        self.assertEqual({'id': 194693}, result)

    def test_find_saas_replication_price_with_iops(self):
        package = {
            'items': [
                {
                    'keyName': 'REPLICATION_FOR_IOPSBASED_PERFORMANCE',
                    'prices': [
                        {
                            'capacityRestrictionMaximum': '48000',
                            'capacityRestrictionMinimum': '1',
                            'capacityRestrictionType': 'IOPS',
                            'categories': [
                                {'categoryCode':
                                    'performance_storage_replication'}
                            ],
                            'id': 192033,
                            'locationGroupId': ''
                        }
                    ]
                }
            ]
        }

        result = storage_utils.find_saas_replication_price(
            package, iops=800
        )

        self.assertEqual({'id': 192033}, result)

    # ---------------------------------------------------------------------
    # Tests for find_snapshot_schedule_id()
    # ---------------------------------------------------------------------
    def test_find_snapshot_schedule_id_no_schedules(self):
        volume = {
            'schedules': []
        }

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_snapshot_schedule_id,
            volume, 'SNAPSHOT_WEEKLY'
        )

        self.assertEqual(
            "The given snapshot schedule ID was not found for "
            "the given storage volume",
            str(exception)
        )

    def test_find_snapshot_schedule_id_no_type_in_schedule(self):
        volume = {
            'schedules': [
                {'id': 888}
            ]
        }

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_snapshot_schedule_id,
            volume, 'SNAPSHOT_WEEKLY'
        )

        self.assertEqual(
            "The given snapshot schedule ID was not found for "
            "the given storage volume",
            str(exception)
        )

    def test_find_snapshot_schedule_id_no_keyname_in_schedule_type(self):
        volume = {
            'schedules': [
                {
                    'id': 888,
                    'type': {}
                }
            ]
        }

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_snapshot_schedule_id,
            volume, 'SNAPSHOT_WEEKLY'
        )

        self.assertEqual(
            "The given snapshot schedule ID was not found for "
            "the given storage volume",
            str(exception)
        )

    def test_find_snapshot_schedule_id_no_matching_keyname(self):
        volume = {
            'schedules': [
                {
                    'id': 888,
                    'type': {'keyname': 'SNAPSHOT_DAILY'}
                }
            ]
        }

        exception = self.assertRaises(
            ValueError,
            storage_utils.find_snapshot_schedule_id,
            volume, 'SNAPSHOT_WEEKLY'
        )

        self.assertEqual(
            "The given snapshot schedule ID was not found for "
            "the given storage volume",
            str(exception)
        )

    def test_find_snapshot_schedule_id(self):
        volume = {
            'schedules': [
                {
                    'id': 888,
                    'type': {'keyname': 'SNAPSHOT_DAILY'}
                }, {
                    'id': 999,
                    'type': {'keyname': 'SNAPSHOT_WEEKLY'}
                }
            ]
        }

        result = storage_utils.find_snapshot_schedule_id(
            volume, 'SNAPSHOT_WEEKLY'
        )

        self.assertEqual(999, result)

    # ---------------------------------------------------------------------
    # Tests for prepare_snapshot_order_object()
    # ---------------------------------------------------------------------
    def test_prep_snapshot_order_billing_item_cancelled(self):
        mock_volume = copy.deepcopy(SoftLayer_Network_Storage.STAAS_TEST_VOLUME)
        del mock_volume['billingItem']

        exception = self.assertRaises(
            exceptions.SoftLayerError,
            storage_utils.prepare_snapshot_order_object,
            self.block, mock_volume, 10, None, False
        )

        self.assertEqual(
            "This volume has been cancelled; unable to order snapshot space",
            str(exception)
        )

    def test_prep_snapshot_order_invalid_billing_item_category_code(self):
        mock_volume = copy.deepcopy(SoftLayer_Network_Storage.STAAS_TEST_VOLUME)
        mock_volume['billingItem']['categoryCode'] = 'invalid_type_ninja_cat'

        exception = self.assertRaises(
            exceptions.SoftLayerError,
            storage_utils.prepare_snapshot_order_object,
            self.block, mock_volume, 10, None, False
        )

        self.assertEqual(
            "Snapshot space cannot be ordered for a primary volume with a "
            "billing item category code of 'invalid_type_ninja_cat'",
            str(exception)
        )

    def test_prep_snapshot_order_saas_endurance_tier_is_not_none(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [SoftLayer_Product_Package.SAAS_PACKAGE]

        mock_volume = SoftLayer_Network_Storage.STAAS_TEST_VOLUME

        expected_object = {
            'complexType': 'SoftLayer_Container_Product_Order_'
                           'Network_Storage_Enterprise_SnapshotSpace',
            'packageId': 759,
            'prices': [{'id': 193613}],
            'quantity': 1,
            'location': 449500,
            'volumeId': 102,
            'useHourlyPricing': False
        }

        result = storage_utils.prepare_snapshot_order_object(
            self.block, mock_volume, 10, 2, False
        )

        self.assertEqual(expected_object, result)

    def test_prep_snapshot_order_saas_endurance_upgrade(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [SoftLayer_Product_Package.SAAS_PACKAGE]

        mock_volume = SoftLayer_Network_Storage.STAAS_TEST_VOLUME

        expected_object = {
            'complexType': 'SoftLayer_Container_Product_Order_'
                           'Network_Storage_Enterprise_SnapshotSpace_Upgrade',
            'packageId': 759,
            'prices': [{'id': 193853}],
            'quantity': 1,
            'location': 449500,
            'volumeId': 102,
            'useHourlyPricing': False
        }

        result = storage_utils.prepare_snapshot_order_object(
            self.block, mock_volume, 20, None, True
        )

        self.assertEqual(expected_object, result)

    def test_prep_snapshot_order_saas_performance_volume_below_staas_v2(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [SoftLayer_Product_Package.SAAS_PACKAGE]

        mock_volume = copy.deepcopy(SoftLayer_Network_Storage.STAAS_TEST_VOLUME)
        mock_volume['storageType']['keyName'] = 'PERFORMANCE_BLOCK_STORAGE'
        mock_volume['staasVersion'] = '1'

        exception = self.assertRaises(
            exceptions.SoftLayerError,
            storage_utils.prepare_snapshot_order_object,
            self.block, mock_volume, 10, None, False
        )

        self.assertEqual(
            "Snapshot space cannot be ordered for this performance "
            "volume since it does not support Encryption at Rest.",
            str(exception)
        )

    def test_prep_snapshot_order_saas_performance(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [SoftLayer_Product_Package.SAAS_PACKAGE]

        mock_volume = copy.deepcopy(SoftLayer_Network_Storage.STAAS_TEST_VOLUME)
        mock_volume['storageType']['keyName'] = 'PERFORMANCE_BLOCK_STORAGE'

        expected_object = {
            'complexType': 'SoftLayer_Container_Product_Order_'
                           'Network_Storage_Enterprise_SnapshotSpace',
            'packageId': 759,
            'prices': [{'id': 191193}],
            'quantity': 1,
            'location': 449500,
            'volumeId': 102,
            'useHourlyPricing': False
        }

        result = storage_utils.prepare_snapshot_order_object(
            self.block, mock_volume, 10, None, False
        )

        self.assertEqual(expected_object, result)

    def test_prep_snapshot_order_saas_invalid_storage_type(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [SoftLayer_Product_Package.SAAS_PACKAGE]

        mock_volume = copy.deepcopy(SoftLayer_Network_Storage.STAAS_TEST_VOLUME)
        mock_volume['storageType']['keyName'] = 'TASTY_PASTA_STORAGE'

        exception = self.assertRaises(
            exceptions.SoftLayerError,
            storage_utils.prepare_snapshot_order_object,
            self.block, mock_volume, 10, None, False
        )

        self.assertEqual(
            "Storage volume does not have a valid storage type "
            "(with an appropriate keyName to indicate the "
            "volume is a PERFORMANCE or an ENDURANCE volume)",
            str(exception)
        )

    def test_prep_snapshot_order_enterprise_tier_is_not_none(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [
            SoftLayer_Product_Package.ENTERPRISE_PACKAGE
        ]

        mock_volume = SoftLayer_Network_Storage.getObject

        expected_object = {
            'complexType': 'SoftLayer_Container_Product_Order_'
                           'Network_Storage_Enterprise_SnapshotSpace',
            'packageId': 240,
            'prices': [{'id': 46160}],
            'quantity': 1,
            'location': 449500,
            'volumeId': 100,
            'useHourlyPricing': False
        }

        result = storage_utils.prepare_snapshot_order_object(
            self.block, mock_volume, 10, 2, False
        )

        self.assertEqual(expected_object, result)

    def test_prep_snapshot_order_enterprise(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [
            SoftLayer_Product_Package.ENTERPRISE_PACKAGE
        ]

        mock_volume = SoftLayer_Network_Storage.getObject

        expected_object = {
            'complexType': 'SoftLayer_Container_Product_Order_'
                           'Network_Storage_Enterprise_SnapshotSpace',
            'packageId': 240,
            'prices': [{'id': 45860}],
            'quantity': 1,
            'location': 449500,
            'volumeId': 100,
            'useHourlyPricing': False
        }

        result = storage_utils.prepare_snapshot_order_object(
            self.block, mock_volume, 20, None, False
        )

        self.assertEqual(expected_object, result)

    def test_prep_snapshot_order_hourly_billing(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [SoftLayer_Product_Package.SAAS_PACKAGE]

        mock_volume = copy.deepcopy(SoftLayer_Network_Storage.STAAS_TEST_VOLUME)
        mock_volume['billingItem']['hourlyFlag'] = True

        expected_object = {
            'complexType': 'SoftLayer_Container_Product_Order_'
                           'Network_Storage_Enterprise_SnapshotSpace',
            'packageId': 759,
            'prices': [{'id': 193853}],
            'quantity': 1,
            'location': 449500,
            'volumeId': 102,
            'useHourlyPricing': True
        }

        result = storage_utils.prepare_snapshot_order_object(
            self.block, mock_volume, 20, None, False
        )

        self.assertEqual(expected_object, result)

    # ---------------------------------------------------------------------
    # Tests for prepare_volume_order_object()
    # ---------------------------------------------------------------------
    def test_prep_volume_order_invalid_storage_type(self):
        exception = self.assertRaises(
            exceptions.SoftLayerError,
            storage_utils.prepare_volume_order_object,
            self.block, 'saxophone_cat', 'dal09', 1000,
            None, 4, None, 'enterprise', 'block'
        )

        self.assertEqual(
            "Volume storage type must be either performance or endurance",
            str(exception)
        )

    def test_prep_volume_order_invalid_location(self):
        mock = self.set_mock('SoftLayer_Location_Datacenter', 'getDatacenters')
        mock.return_value = []

        exception = self.assertRaises(
            exceptions.SoftLayerError,
            storage_utils.prepare_volume_order_object,
            self.block, 'endurance', 'hoth01', 1000,
            None, 4, None, 'enterprise', 'block'
        )

        self.assertEqual(
            "Invalid datacenter name specified. "
            "Please provide the lower case short name (e.g.: dal09)",
            str(exception)
        )

    def test_prep_volume_order_enterprise_offering_invalid_storage_type(self):
        mock = self.set_mock('SoftLayer_Location_Datacenter', 'getDatacenters')
        mock.return_value = [{'id': 29, 'name': 'dal09'}]

        exception = self.assertRaises(
            exceptions.SoftLayerError,
            storage_utils.prepare_volume_order_object,
            self.block, 'performance', 'dal09', 1000,
            None, 4, None, 'enterprise', 'block'
        )

        self.assertEqual(
            "The requested offering package, 'enterprise', is not "
            "available for the 'performance' storage type.",
            str(exception)
        )

    def test_prep_volume_order_performance_offering_invalid_storage_type(self):
        mock = self.set_mock('SoftLayer_Location_Datacenter', 'getDatacenters')
        mock.return_value = [{'id': 29, 'name': 'dal09'}]

        exception = self.assertRaises(
            exceptions.SoftLayerError,
            storage_utils.prepare_volume_order_object,
            self.block, 'endurance', 'dal09', 1000,
            800, None, None, 'performance', 'block'
        )

        self.assertEqual(
            "The requested offering package, 'performance', is not "
            "available for the 'endurance' storage type.",
            str(exception)
        )

    def test_prep_volume_order_invalid_offering(self):
        mock = self.set_mock('SoftLayer_Location_Datacenter', 'getDatacenters')
        mock.return_value = [{'id': 29, 'name': 'dal09'}]

        exception = self.assertRaises(
            exceptions.SoftLayerError,
            storage_utils.prepare_volume_order_object,
            self.block, 'endurance', 'dal09', 1000,
            None, 4, None, 'jazz_penguins', 'block'
        )

        self.assertEqual(
            "The requested service offering package is not valid. "
            "Please check the available options and try again.",
            str(exception)
        )

    def test_prep_volume_order_saas_performance(self):
        mock = self.set_mock('SoftLayer_Location_Datacenter', 'getDatacenters')
        mock.return_value = [{'id': 29, 'name': 'dal09'}]
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [SoftLayer_Product_Package.SAAS_PACKAGE]

        expected_object = {
            'complexType': 'SoftLayer_Container_Product_Order_'
                           'Network_Storage_AsAService',
            'packageId': 759,
            'prices': [
                {'id': 189433},
                {'id': 189453},
                {'id': 190113},
                {'id': 190173}
            ],
            'quantity': 1,
            'location': 29,
            'volumeSize': 1000,
            'iops': 800,
            'useHourlyPricing': False
        }

        result = storage_utils.prepare_volume_order_object(
            self.file, 'performance', 'dal09', 1000,
            800, None, None, 'storage_as_a_service', 'file'
        )

        self.assertEqual(expected_object, result)

    def test_prep_volume_order_saas_performance_rest(self):
        mock = self.set_mock('SoftLayer_Location_Datacenter', 'getDatacenters')
        mock.return_value = [{'id': 29, 'name': 'dal09'}]
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [SoftLayer_Product_Package.SAAS_REST_PACKAGE]

        expected_object = {
            'complexType': 'SoftLayer_Container_Product_Order_'
                           'Network_Storage_AsAService',
            'packageId': 759,
            'prices': [
                {'id': 189433},
                {'id': 189453},
                {'id': 190113},
                {'id': 190173}
            ],
            'quantity': 1,
            'location': 29,
            'volumeSize': 1000,
            'iops': 800,
            'useHourlyPricing': False
        }

        result = storage_utils.prepare_volume_order_object(
            self.file, 'performance', 'dal09', 1000,
            800, None, None, 'storage_as_a_service', 'file'
        )

        self.assertEqual(expected_object, result)

    def test_prep_volume_order_saas_performance_with_snapshot(self):
        mock = self.set_mock('SoftLayer_Location_Datacenter', 'getDatacenters')
        mock.return_value = [{'id': 29, 'name': 'dal09'}]
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [SoftLayer_Product_Package.SAAS_PACKAGE]

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
            'quantity': 1,
            'location': 29,
            'volumeSize': 1000,
            'iops': 800,
            'useHourlyPricing': False
        }

        result = storage_utils.prepare_volume_order_object(
            self.file, 'performance', 'dal09', 1000,
            800, None, 10, 'storage_as_a_service', 'file'
        )

        self.assertEqual(expected_object, result)

    def test_prep_volume_order_saas_endurance(self):
        mock = self.set_mock('SoftLayer_Location_Datacenter', 'getDatacenters')
        mock.return_value = [{'id': 29, 'name': 'dal09'}]
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [SoftLayer_Product_Package.SAAS_PACKAGE]

        expected_object = {
            'complexType': 'SoftLayer_Container_Product_Order_'
                           'Network_Storage_AsAService',
            'packageId': 759,
            'prices': [
                {'id': 189433},
                {'id': 189443},
                {'id': 194763},
                {'id': 194703}
            ],
            'quantity': 1,
            'location': 29,
            'volumeSize': 1000,
            'useHourlyPricing': False
        }

        result = storage_utils.prepare_volume_order_object(
            self.block, 'endurance', 'dal09', 1000,
            None, 4, None, 'storage_as_a_service', 'block'
        )

        self.assertEqual(expected_object, result)

    def test_prep_volume_order_saas_endurance_with_snapshot(self):
        mock = self.set_mock('SoftLayer_Location_Datacenter', 'getDatacenters')
        mock.return_value = [{'id': 29, 'name': 'dal09'}]
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [SoftLayer_Product_Package.SAAS_PACKAGE]

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
            'quantity': 1,
            'location': 29,
            'volumeSize': 1000,
            'useHourlyPricing': False
        }

        result = storage_utils.prepare_volume_order_object(
            self.block, 'endurance', 'dal09', 1000,
            None, 4, 10, 'storage_as_a_service', 'block'
        )

        self.assertEqual(expected_object, result)

    def test_prep_volume_order_perf_performance_block(self):
        mock = self.set_mock('SoftLayer_Location_Datacenter', 'getDatacenters')
        mock.return_value = [{'id': 29, 'name': 'dal09'}]
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [
            SoftLayer_Product_Package.PERFORMANCE_PACKAGE
        ]

        expected_object = {
            'complexType': 'SoftLayer_Container_Product_Order_'
                           'Network_PerformanceStorage_Iscsi',
            'packageId': 222,
            'prices': [
                {'id': 40672},
                {'id': 40742},
                {'id': 41562}
            ],
            'quantity': 1,
            'location': 29,
            'useHourlyPricing': False
        }

        result = storage_utils.prepare_volume_order_object(
            self.block, 'performance', 'dal09', 1000,
            800, None, None, 'performance', 'block'
        )

        self.assertEqual(expected_object, result)

    def test_prep_volume_order_perf_performance_file(self):
        mock = self.set_mock('SoftLayer_Location_Datacenter', 'getDatacenters')
        mock.return_value = [{'id': 29, 'name': 'dal09'}]
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [
            SoftLayer_Product_Package.PERFORMANCE_PACKAGE
        ]

        expected_object = {
            'complexType': 'SoftLayer_Container_Product_Order_'
                           'Network_PerformanceStorage_Nfs',
            'packageId': 222,
            'prices': [
                {'id': 40662},
                {'id': 40742},
                {'id': 41562}
            ],
            'quantity': 1,
            'location': 29,
            'useHourlyPricing': False
        }

        result = storage_utils.prepare_volume_order_object(
            self.file, 'performance', 'dal09', 1000,
            800, None, None, 'performance', 'file'
        )

        self.assertEqual(expected_object, result)

    def test_prep_volume_order_ent_endurance(self):
        mock = self.set_mock('SoftLayer_Location_Datacenter', 'getDatacenters')
        mock.return_value = [{'id': 29, 'name': 'dal09'}]
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [
            SoftLayer_Product_Package.ENTERPRISE_PACKAGE
        ]

        expected_object = {
            'complexType': 'SoftLayer_Container_Product_Order_'
                           'Network_Storage_Enterprise',
            'packageId': 240,
            'prices': [
                {'id': 45058},
                {'id': 45108},
                {'id': 45318},
                {'id': 45088}
            ],
            'quantity': 1,
            'location': 29,
            'useHourlyPricing': False
        }

        result = storage_utils.prepare_volume_order_object(
            self.file, 'endurance', 'dal09', 1000,
            None, 4, None, 'enterprise', 'file'
        )

        self.assertEqual(expected_object, result)

    def test_prep_volume_order_ent_endurance_with_snapshot(self):
        mock = self.set_mock('SoftLayer_Location_Datacenter', 'getDatacenters')
        mock.return_value = [{'id': 29, 'name': 'dal09'}]
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [
            SoftLayer_Product_Package.ENTERPRISE_PACKAGE
        ]

        expected_object = {
            'complexType': 'SoftLayer_Container_Product_Order_'
                           'Network_Storage_Enterprise',
            'packageId': 240,
            'prices': [
                {'id': 45058},
                {'id': 45098},
                {'id': 45318},
                {'id': 45088},
                {'id': 46170}
            ],
            'quantity': 1,
            'location': 29,
            'useHourlyPricing': False
        }

        result = storage_utils.prepare_volume_order_object(
            self.block, 'endurance', 'dal09', 1000,
            None, 4, 10, 'enterprise', 'block'
        )

        self.assertEqual(expected_object, result)

    # ---------------------------------------------------------------------
    # Tests for prepare_replicant_order_object()
    # ---------------------------------------------------------------------
    def test_prep_replicant_order_volume_cancelled(self):
        mock_volume = copy.deepcopy(SoftLayer_Network_Storage.STAAS_TEST_VOLUME)
        del mock_volume['billingItem']

        exception = self.assertRaises(
            exceptions.SoftLayerError,
            storage_utils.prepare_replicant_order_object,
            self.block, 'WEEKLY', 'wdc04', None, mock_volume, 'block'
        )

        self.assertEqual(
            'This volume is set for cancellation; '
            'unable to order replicant volume',
            str(exception)
        )

    def test_prep_replicant_order_volume_cancellation_date_set(self):
        mock_volume = copy.deepcopy(SoftLayer_Network_Storage.STAAS_TEST_VOLUME)
        mock_volume['billingItem']['cancellationDate'] = 'y2k, oh nooooo'

        exception = self.assertRaises(
            exceptions.SoftLayerError,
            storage_utils.prepare_replicant_order_object,
            self.block, 'WEEKLY', 'wdc04', None, mock_volume, 'block'
        )

        self.assertEqual(
            'This volume is set for cancellation; '
            'unable to order replicant volume',
            str(exception)
        )

    def test_prep_replicant_order_snapshot_space_cancelled(self):
        mock_volume = copy.deepcopy(SoftLayer_Network_Storage.STAAS_TEST_VOLUME)
        snapshot_billing_item = mock_volume['billingItem']['activeChildren'][0]
        snapshot_billing_item['cancellationDate'] = 'daylight saving time, no!'

        exception = self.assertRaises(
            exceptions.SoftLayerError,
            storage_utils.prepare_replicant_order_object,
            self.block, 'WEEKLY', 'wdc04', None, mock_volume, 'block'
        )

        self.assertEqual(
            'The snapshot space for this volume is set for '
            'cancellation; unable to order replicant volume',
            str(exception)
        )

    def test_prep_replicant_order_invalid_location(self):
        mock = self.set_mock('SoftLayer_Location_Datacenter', 'getDatacenters')
        mock.return_value = []

        mock_volume = SoftLayer_Network_Storage.STAAS_TEST_VOLUME

        exception = self.assertRaises(
            exceptions.SoftLayerError,
            storage_utils.prepare_replicant_order_object,
            self.block, 'WEEKLY', 'hoth02', None, mock_volume, 'block'
        )

        self.assertEqual(
            "Invalid datacenter name specified. "
            "Please provide the lower case short name (e.g.: dal09)",
            str(exception)
        )

    def test_prep_replicant_order_enterprise_offering_invalid_type(self):
        mock = self.set_mock('SoftLayer_Location_Datacenter', 'getDatacenters')
        mock.return_value = [{'id': 51, 'name': 'wdc04'}]

        mock_volume = copy.deepcopy(SoftLayer_Network_Storage.STAAS_TEST_VOLUME)
        mock_volume['billingItem']['categoryCode'] = 'invalid_type_ninja_cat'

        exception = self.assertRaises(
            exceptions.SoftLayerError,
            storage_utils.prepare_replicant_order_object,
            self.block, 'WEEKLY', 'wdc04', None, mock_volume, 'block'
        )

        self.assertEqual(
            "A replicant volume cannot be ordered for a primary volume with a "
            "billing item category code of 'invalid_type_ninja_cat'",
            str(exception)
        )

    def test_prep_replicant_order_snapshot_capacity_not_found(self):
        mock = self.set_mock('SoftLayer_Location_Datacenter', 'getDatacenters')
        mock.return_value = [{'id': 51, 'name': 'wdc04'}]

        mock_volume = copy.deepcopy(SoftLayer_Network_Storage.STAAS_TEST_VOLUME)
        del mock_volume['snapshotCapacityGb']

        exception = self.assertRaises(
            exceptions.SoftLayerError,
            storage_utils.prepare_replicant_order_object,
            self.block, 'WEEKLY', 'wdc04', None, mock_volume, 'block'
        )

        self.assertEqual(
            "Snapshot capacity not found for the given primary volume",
            str(exception)
        )

    def test_prep_replicant_order_saas_endurance(self):
        mock = self.set_mock('SoftLayer_Location_Datacenter', 'getDatacenters')
        mock.return_value = [{'id': 51, 'name': 'wdc04'}]
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [SoftLayer_Product_Package.SAAS_PACKAGE]

        mock_volume = SoftLayer_Network_Storage.STAAS_TEST_VOLUME

        expected_object = {
            'complexType': 'SoftLayer_Container_Product_Order_'
                           'Network_Storage_AsAService',
            'packageId': 759,
            'prices': [
                {'id': 189433},
                {'id': 189443},
                {'id': 193433},
                {'id': 193373},
                {'id': 193613},
                {'id': 194693}
            ],
            'quantity': 1,
            'location': 51,
            'originVolumeId': 102,
            'originVolumeScheduleId': 978,
            'volumeSize': 500,
            'useHourlyPricing': False
        }

        result = storage_utils.prepare_replicant_order_object(
            self.block, 'WEEKLY', 'wdc04', None, mock_volume, 'block'
        )

        self.assertEqual(expected_object, result)

    def test_prep_replicant_order_saas_endurance_tier_is_not_none(self):
        mock = self.set_mock('SoftLayer_Location_Datacenter', 'getDatacenters')
        mock.return_value = [{'id': 51, 'name': 'wdc04'}]
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [SoftLayer_Product_Package.SAAS_PACKAGE]

        mock_volume = SoftLayer_Network_Storage.STAAS_TEST_VOLUME

        expected_object = {
            'complexType': 'SoftLayer_Container_Product_Order_'
                           'Network_Storage_AsAService',
            'packageId': 759,
            'prices': [
                {'id': 189433},
                {'id': 189443},
                {'id': 193433},
                {'id': 193373},
                {'id': 193613},
                {'id': 194693}
            ],
            'quantity': 1,
            'location': 51,
            'originVolumeId': 102,
            'originVolumeScheduleId': 978,
            'volumeSize': 500,
            'useHourlyPricing': False
        }

        result = storage_utils.prepare_replicant_order_object(
            self.block, 'WEEKLY', 'wdc04', 2, mock_volume, 'block'
        )

        self.assertEqual(expected_object, result)

    def test_prep_replicant_order_saas_performance_volume_below_staas_v2(self):
        mock = self.set_mock('SoftLayer_Location_Datacenter', 'getDatacenters')
        mock.return_value = [{'id': 51, 'name': 'wdc04'}]
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [SoftLayer_Product_Package.SAAS_PACKAGE]

        mock_volume = copy.deepcopy(SoftLayer_Network_Storage.STAAS_TEST_VOLUME)
        mock_volume['storageType']['keyName'] = 'PERFORMANCE_BLOCK_STORAGE'
        mock_volume['hasEncryptionAtRest'] = 0

        exception = self.assertRaises(
            exceptions.SoftLayerError,
            storage_utils.prepare_replicant_order_object,
            self.block, 'WEEKLY', 'wdc04', None, mock_volume, 'block'
        )

        self.assertEqual(
            "A replica volume cannot be ordered for this performance "
            "volume since it does not support Encryption at Rest.",
            str(exception)
        )

    def test_prep_replicant_order_saas_performance(self):
        mock = self.set_mock('SoftLayer_Location_Datacenter', 'getDatacenters')
        mock.return_value = [{'id': 51, 'name': 'wdc04'}]
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [SoftLayer_Product_Package.SAAS_PACKAGE]

        mock_volume = copy.deepcopy(SoftLayer_Network_Storage.STAAS_TEST_VOLUME)
        mock_volume['storageType']['keyName'] = 'PERFORMANCE_BLOCK_STORAGE'

        expected_object = {
            'complexType': 'SoftLayer_Container_Product_Order_'
                           'Network_Storage_AsAService',
            'packageId': 759,
            'prices': [
                {'id': 189433},
                {'id': 189443},
                {'id': 189993},
                {'id': 190053},
                {'id': 191193},
                {'id': 192033}
            ],
            'quantity': 1,
            'location': 51,
            'originVolumeId': 102,
            'originVolumeScheduleId': 978,
            'volumeSize': 500,
            'iops': 1000,
            'useHourlyPricing': False
        }

        result = storage_utils.prepare_replicant_order_object(
            self.block, 'WEEKLY', 'wdc04', None, mock_volume, 'block'
        )

        self.assertEqual(expected_object, result)

    def test_prep_replicant_order_saas_invalid_storage_type(self):
        mock = self.set_mock('SoftLayer_Location_Datacenter', 'getDatacenters')
        mock.return_value = [{'id': 51, 'name': 'wdc04'}]
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [SoftLayer_Product_Package.SAAS_PACKAGE]

        mock_volume = copy.deepcopy(SoftLayer_Network_Storage.STAAS_TEST_VOLUME)
        mock_volume['storageType']['keyName'] = 'CATS_LIKE_PIANO_MUSIC'

        exception = self.assertRaises(
            exceptions.SoftLayerError,
            storage_utils.prepare_replicant_order_object,
            self.block, 'WEEKLY', 'wdc04', None, mock_volume, 'block'
        )

        self.assertEqual(
            "Storage volume does not have a valid storage type "
            "(with an appropriate keyName to indicate the "
            "volume is a PERFORMANCE or an ENDURANCE volume)",
            str(exception)
        )

    def test_prep_replicant_order_ent_endurance(self):
        mock = self.set_mock('SoftLayer_Location_Datacenter', 'getDatacenters')
        mock.return_value = [{'id': 51, 'name': 'wdc04'}]
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [
            SoftLayer_Product_Package.ENTERPRISE_PACKAGE
        ]

        mock_volume = SoftLayer_Network_Storage.getObject

        expected_object = {
            'complexType': 'SoftLayer_Container_Product_Order_'
                           'Network_Storage_Enterprise',
            'packageId': 240,
            'prices': [
                {'id': 45058},
                {'id': 45098},
                {'id': 45128},
                {'id': 45078},
                {'id': 46160},
                {'id': 46659}
            ],
            'quantity': 1,
            'location': 51,
            'originVolumeId': 100,
            'originVolumeScheduleId': 978,
            'useHourlyPricing': False
        }

        result = storage_utils.prepare_replicant_order_object(
            self.block, 'WEEKLY', 'wdc04', None, mock_volume, 'block'
        )

        self.assertEqual(expected_object, result)

    def test_prep_replicant_order_ent_endurance_tier_is_not_none(self):
        mock = self.set_mock('SoftLayer_Location_Datacenter', 'getDatacenters')
        mock.return_value = [{'id': 51, 'name': 'wdc04'}]
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [
            SoftLayer_Product_Package.ENTERPRISE_PACKAGE
        ]

        mock_volume = SoftLayer_Network_Storage.getObject

        expected_object = {
            'complexType': 'SoftLayer_Container_Product_Order_'
                           'Network_Storage_Enterprise',
            'packageId': 240,
            'prices': [
                {'id': 45058},
                {'id': 45098},
                {'id': 45128},
                {'id': 45078},
                {'id': 46160},
                {'id': 46659}
            ],
            'quantity': 1,
            'location': 51,
            'originVolumeId': 100,
            'originVolumeScheduleId': 978,
            'useHourlyPricing': False
        }

        result = storage_utils.prepare_replicant_order_object(
            self.block, 'WEEKLY', 'wdc04', 2, mock_volume, 'block'
        )

        self.assertEqual(expected_object, result)

    def test_prep_replicant_order_hourly_billing(self):
        mock = self.set_mock('SoftLayer_Location_Datacenter', 'getDatacenters')
        mock.return_value = [{'id': 51, 'name': 'wdc04'}]
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [SoftLayer_Product_Package.SAAS_PACKAGE]

        mock_volume = copy.deepcopy(SoftLayer_Network_Storage.STAAS_TEST_VOLUME)
        mock_volume['billingItem']['hourlyFlag'] = True

        expected_object = {
            'complexType': 'SoftLayer_Container_Product_Order_'
                           'Network_Storage_AsAService',
            'packageId': 759,
            'prices': [
                {'id': 189433},
                {'id': 189443},
                {'id': 193433},
                {'id': 193373},
                {'id': 193613},
                {'id': 194693}
            ],
            'quantity': 1,
            'location': 51,
            'originVolumeId': 102,
            'originVolumeScheduleId': 978,
            'volumeSize': 500,
            'useHourlyPricing': True
        }

        result = storage_utils.prepare_replicant_order_object(
            self.block, 'WEEKLY', 'wdc04', None, mock_volume, 'block'
        )

        self.assertEqual(expected_object, result)

    # ---------------------------------------------------------------------
    # Tests for prepare_duplicate_order_object()
    # ---------------------------------------------------------------------
    def test_prep_duplicate_order_origin_volume_cancelled(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [SoftLayer_Product_Package.SAAS_PACKAGE]

        mock_volume = copy.deepcopy(SoftLayer_Network_Storage.STAAS_TEST_VOLUME)
        del mock_volume['billingItem']

        exception = self.assertRaises(
            exceptions.SoftLayerError,
            storage_utils.prepare_duplicate_order_object,
            self.block, mock_volume, None, None, None, None, 'block'
        )

        self.assertEqual(str(exception),
                         "The origin volume has been cancelled; "
                         "unable to order duplicate volume")

    def test_prep_duplicate_order_origin_snapshot_capacity_not_found(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [SoftLayer_Product_Package.SAAS_PACKAGE]

        mock_volume = copy.deepcopy(SoftLayer_Network_Storage.STAAS_TEST_VOLUME)
        del mock_volume['snapshotCapacityGb']

        exception = self.assertRaises(
            exceptions.SoftLayerError,
            storage_utils.prepare_duplicate_order_object,
            self.block, mock_volume, None, None, None, None, 'block'
        )

        self.assertEqual(str(exception),
                         "Snapshot space not found for the origin volume. "
                         "Origin snapshot space is needed for duplication.")

    def test_prep_duplicate_order_origin_volume_location_not_found(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [SoftLayer_Product_Package.SAAS_PACKAGE]

        mock_volume = copy.deepcopy(SoftLayer_Network_Storage.STAAS_TEST_VOLUME)
        del mock_volume['billingItem']['location']

        exception = self.assertRaises(
            exceptions.SoftLayerError,
            storage_utils.prepare_duplicate_order_object,
            self.block, mock_volume, None, None, None, None, 'block'
        )

        self.assertEqual(str(exception),
                         "Cannot find origin volume's location")

    def test_prep_duplicate_order_origin_volume_staas_version_below_v2(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [SoftLayer_Product_Package.SAAS_PACKAGE]

        mock_volume = copy.deepcopy(SoftLayer_Network_Storage.STAAS_TEST_VOLUME)
        mock_volume['staasVersion'] = 1

        exception = self.assertRaises(
            exceptions.SoftLayerError,
            storage_utils.prepare_duplicate_order_object,
            self.block, mock_volume, None, None, None, None, 'block'
        )

        self.assertEqual("This volume cannot be duplicated since it "
                         "does not support Encryption at Rest.",
                         str(exception))

    def test_prep_duplicate_order_performance_origin_iops_not_found(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [SoftLayer_Product_Package.SAAS_PACKAGE]

        mock_volume = copy.deepcopy(SoftLayer_Network_Storage.STAAS_TEST_VOLUME)
        mock_volume['storageType']['keyName'] = 'PERFORMANCE_BLOCK_STORAGE_REPLICANT'
        del mock_volume['provisionedIops']

        exception = self.assertRaises(
            exceptions.SoftLayerError,
            storage_utils.prepare_duplicate_order_object,
            self.block, mock_volume, None, None, None, None, 'block'
        )

        self.assertEqual(str(exception),
                         "Cannot find origin volume's provisioned IOPS")

    def test_prep_duplicate_order_performance_use_default_origin_values(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [SoftLayer_Product_Package.SAAS_PACKAGE]

        mock_volume = copy.deepcopy(SoftLayer_Network_Storage.STAAS_TEST_VOLUME)
        mock_volume['storageType']['keyName'] = 'PERFORMANCE_FILE_STORAGE_REPLICANT'

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
            'iops': 1000,
            'useHourlyPricing': False}

        result = storage_utils.prepare_duplicate_order_object(
            self.file, mock_volume, None, None, None, None, 'file')

        self.assertEqual(expected_object, result)

    def test_prep_duplicate_order_performance_block(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [SoftLayer_Product_Package.SAAS_PACKAGE]

        mock_volume = copy.deepcopy(SoftLayer_Network_Storage.STAAS_TEST_VOLUME)
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
            'iops': 2000,
            'useHourlyPricing': False}

        result = storage_utils.prepare_duplicate_order_object(
            self.block, mock_volume, 2000, None, 1000, 10, 'block')

        self.assertEqual(expected_object, result)

    def test_prep_duplicate_order_performance_file(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [SoftLayer_Product_Package.SAAS_PACKAGE]

        mock_volume = copy.deepcopy(SoftLayer_Network_Storage.STAAS_TEST_VOLUME)
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
            'iops': 2000,
            'useHourlyPricing': False}

        result = storage_utils.prepare_duplicate_order_object(
            self.file, mock_volume, 2000, None, 1000, 10, 'file')

        self.assertEqual(expected_object, result)

    def test_prep_duplicate_order_endurance_use_default_origin_values(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [SoftLayer_Product_Package.SAAS_PACKAGE]

        mock_volume = copy.deepcopy(SoftLayer_Network_Storage.STAAS_TEST_VOLUME)
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
            'duplicateOriginVolumeId': 102,
            'useHourlyPricing': False}

        result = storage_utils.prepare_duplicate_order_object(
            self.file, mock_volume, None, None, None, None, 'file')

        self.assertEqual(expected_object, result)

    def test_prep_duplicate_order_endurance_block(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [SoftLayer_Product_Package.SAAS_PACKAGE]

        mock_volume = SoftLayer_Network_Storage.STAAS_TEST_VOLUME

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
            'duplicateOriginVolumeId': 102,
            'useHourlyPricing': False}

        result = storage_utils.prepare_duplicate_order_object(
            self.block, mock_volume, None, 4.0, 1000, 10, 'block')

        self.assertEqual(expected_object, result)

    def test_prep_duplicate_order_endurance_file(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [SoftLayer_Product_Package.SAAS_PACKAGE]

        mock_volume = copy.deepcopy(SoftLayer_Network_Storage.STAAS_TEST_VOLUME)
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
            'duplicateOriginVolumeId': 102,
            'useHourlyPricing': False}

        result = storage_utils.prepare_duplicate_order_object(
            self.file, mock_volume, None, 4.0, 1000, 10, 'file')

        self.assertEqual(expected_object, result)

    def test_prep_duplicate_order_invalid_origin_storage_type(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [SoftLayer_Product_Package.SAAS_PACKAGE]

        mock_volume = copy.deepcopy(SoftLayer_Network_Storage.STAAS_TEST_VOLUME)
        mock_volume['storageType']['keyName'] = 'NINJA_CATS'

        exception = self.assertRaises(
            exceptions.SoftLayerError,
            storage_utils.prepare_duplicate_order_object,
            self.block, mock_volume, None, None, None, None, 'block'
        )

        self.assertEqual(str(exception),
                         "Origin volume does not have a valid storage type "
                         "(with an appropriate keyName to indicate the "
                         "volume is a PERFORMANCE or an ENDURANCE volume)")

    # ---------------------------------------------------------------------
    # Tests for prepare_modify_order_object()
    # ---------------------------------------------------------------------
    def test_prep_modify_order_origin_volume_cancelled(self):
        mock_volume = copy.deepcopy(SoftLayer_Network_Storage.STAAS_TEST_VOLUME)
        del mock_volume['billingItem']

        exception = self.assertRaises(exceptions.SoftLayerError, storage_utils.prepare_modify_order_object,
                                      self.block, mock_volume, None, None, None)

        self.assertEqual("The volume has been cancelled; unable to modify volume.", str(exception))

    def test_prep_modify_order_origin_volume_staas_version_below_v2(self):
        mock_volume = copy.deepcopy(SoftLayer_Network_Storage.STAAS_TEST_VOLUME)
        mock_volume['staasVersion'] = 1

        exception = self.assertRaises(exceptions.SoftLayerError, storage_utils.prepare_modify_order_object,
                                      self.block, mock_volume, None, None, None)

        self.assertEqual("This volume cannot be modified since it does not support Encryption at Rest.",
                         str(exception))

    def test_prep_modify_order_performance_values_not_given(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [SoftLayer_Product_Package.SAAS_PACKAGE]

        mock_volume = copy.deepcopy(SoftLayer_Network_Storage.STAAS_TEST_VOLUME)
        mock_volume['storageType']['keyName'] = 'PERFORMANCE_BLOCK_STORAGE'

        exception = self.assertRaises(exceptions.SoftLayerError, storage_utils.prepare_modify_order_object,
                                      self.block, mock_volume, None, None, None)

        self.assertEqual("A size or IOPS value must be given to modify this performance volume.", str(exception))

    def test_prep_modify_order_performance_iops_not_found(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [SoftLayer_Product_Package.SAAS_PACKAGE]

        mock_volume = copy.deepcopy(SoftLayer_Network_Storage.STAAS_TEST_VOLUME)
        mock_volume['storageType']['keyName'] = 'PERFORMANCE_BLOCK_STORAGE'
        del mock_volume['provisionedIops']

        exception = self.assertRaises(exceptions.SoftLayerError, storage_utils.prepare_modify_order_object,
                                      self.block, mock_volume, None, None, 40)

        self.assertEqual("Cannot find volume's provisioned IOPS.", str(exception))

    def test_prep_modify_order_performance_use_existing_iops(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [SoftLayer_Product_Package.SAAS_PACKAGE]

        mock_volume = copy.deepcopy(SoftLayer_Network_Storage.STAAS_TEST_VOLUME)
        mock_volume['storageType']['keyName'] = 'PERFORMANCE_FILE_STORAGE'

        expected_object = {
            'complexType': 'SoftLayer_Container_Product_Order_Network_Storage_AsAService_Upgrade',
            'packageId': 759,
            'prices': [{'id': 189433}, {'id': 190113}, {'id': 190173}],
            'volume': {'id': 102},
            'volumeSize': 1000,
            'iops': 1000
        }

        result = storage_utils.prepare_modify_order_object(self.file, mock_volume, None, None, 1000)
        self.assertEqual(expected_object, result)

    def test_prep_modify_order_performance_use_existing_size(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [SoftLayer_Product_Package.SAAS_PACKAGE]

        mock_volume = copy.deepcopy(SoftLayer_Network_Storage.STAAS_TEST_VOLUME)
        mock_volume['storageType']['keyName'] = 'PERFORMANCE_BLOCK_STORAGE'

        expected_object = {
            'complexType': 'SoftLayer_Container_Product_Order_Network_Storage_AsAService_Upgrade',
            'packageId': 759,
            'prices': [{'id': 189433}, {'id': 189993}, {'id': 190053}],
            'volume': {'id': 102},
            'volumeSize': 500,
            'iops': 2000
        }

        result = storage_utils.prepare_modify_order_object(self.block, mock_volume, 2000, None, None)
        self.assertEqual(expected_object, result)

    def test_prep_modify_order_performance(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [SoftLayer_Product_Package.SAAS_PACKAGE]

        mock_volume = copy.deepcopy(SoftLayer_Network_Storage.STAAS_TEST_VOLUME)
        mock_volume['storageType']['keyName'] = 'PERFORMANCE_FILE_STORAGE'

        expected_object = {
            'complexType': 'SoftLayer_Container_Product_Order_Network_Storage_AsAService_Upgrade',
            'packageId': 759,
            'prices': [{'id': 189433}, {'id': 190113}, {'id': 190173}],
            'volume': {'id': 102},
            'volumeSize': 1000,
            'iops': 2000
        }

        result = storage_utils.prepare_modify_order_object(self.file, mock_volume, 2000, None, 1000)
        self.assertEqual(expected_object, result)

    def test_prep_modify_order_endurance_values_not_given(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [SoftLayer_Product_Package.SAAS_PACKAGE]

        mock_volume = copy.deepcopy(SoftLayer_Network_Storage.STAAS_TEST_VOLUME)
        mock_volume['storageType']['keyName'] = 'ENDURANCE_BLOCK_STORAGE'

        exception = self.assertRaises(exceptions.SoftLayerError, storage_utils.prepare_modify_order_object,
                                      self.block, mock_volume, None, None, None)

        self.assertEqual("A size or tier value must be given to modify this endurance volume.", str(exception))

    def test_prep_modify_order_endurance_use_existing_tier(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [SoftLayer_Product_Package.SAAS_PACKAGE]

        mock_volume = copy.deepcopy(SoftLayer_Network_Storage.STAAS_TEST_VOLUME)
        mock_volume['storageType']['keyName'] = 'ENDURANCE_FILE_STORAGE'

        expected_object = {
            'complexType': 'SoftLayer_Container_Product_Order_Network_Storage_AsAService_Upgrade',
            'packageId': 759,
            'prices': [{'id': 189433}, {'id': 193433}, {'id': 193373}],
            'volume': {'id': 102},
            'volumeSize': 1000
        }

        result = storage_utils.prepare_modify_order_object(self.file, mock_volume, None, None, 1000)
        self.assertEqual(expected_object, result)

    def test_prep_modify_order_endurance_use_existing_size(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [SoftLayer_Product_Package.SAAS_PACKAGE]

        mock_volume = copy.deepcopy(SoftLayer_Network_Storage.STAAS_TEST_VOLUME)
        mock_volume['storageType']['keyName'] = 'ENDURANCE_BLOCK_STORAGE'

        expected_object = {
            'complexType': 'SoftLayer_Container_Product_Order_Network_Storage_AsAService_Upgrade',
            'packageId': 759,
            'prices': [{'id': 189433}, {'id': 194763}, {'id': 194703}],
            'volume': {'id': 102},
            'volumeSize': 500
        }

        result = storage_utils.prepare_modify_order_object(self.block, mock_volume, None, 4, None)
        self.assertEqual(expected_object, result)

    def test_prep_modify_order_endurance(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [SoftLayer_Product_Package.SAAS_PACKAGE]

        mock_volume = copy.deepcopy(SoftLayer_Network_Storage.STAAS_TEST_VOLUME)
        mock_volume['storageType']['keyName'] = 'ENDURANCE_FILE_STORAGE'

        expected_object = {
            'complexType': 'SoftLayer_Container_Product_Order_Network_Storage_AsAService_Upgrade',
            'packageId': 759,
            'prices': [{'id': 189433}, {'id': 194763}, {'id': 194703}],
            'volume': {'id': 102},
            'volumeSize': 1000
        }

        result = storage_utils.prepare_modify_order_object(self.file, mock_volume, None, 4, 1000)
        self.assertEqual(expected_object, result)

    def test_prep_modify_order_invalid_volume_storage_type(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [SoftLayer_Product_Package.SAAS_PACKAGE]

        mock_volume = copy.deepcopy(SoftLayer_Network_Storage.STAAS_TEST_VOLUME)
        mock_volume['storageType']['keyName'] = 'NINJA_PENGUINS'

        exception = self.assertRaises(exceptions.SoftLayerError, storage_utils.prepare_modify_order_object,
                                      self.block, mock_volume, None, None, None)

        self.assertEqual("Volume does not have a valid storage type (with an appropriate "
                         "keyName to indicate the volume is a PERFORMANCE or an ENDURANCE volume).",
                         str(exception))
