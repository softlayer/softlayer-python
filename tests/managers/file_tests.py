"""
    SoftLayer.tests.managers.file_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""

import SoftLayer
from SoftLayer import exceptions
from SoftLayer import fixtures
from SoftLayer import testing


class FileTests(testing.TestCase):
    def set_up(self):
        self.file = SoftLayer.FileStorageManager(self.client)

    def test_cancel_file_volume_immediately(self):
        self.file.cancel_file_volume(123, immediate=True)

        self.assert_called_with(
            'SoftLayer_Billing_Item',
            'cancelItem',
            args=(True, True, 'No longer needed'),
            identifier=449,
        )

    def test_authorize_host_to_volume(self):
        result = self.file.authorize_host_to_volume(
            50,
            hardware_ids=[100],
            virtual_guest_ids=[200],
            ip_address_ids=[300],
            subnet_ids=[400])

        self.assertEqual(fixtures.SoftLayer_Network_Storage.
                         allowAccessFromHostList, result)

        self.assert_called_with(
            'SoftLayer_Network_Storage',
            'allowAccessFromHostList',
            identifier=50)

    def test_deauthorize_host_to_volume(self):
        result = self.file.deauthorize_host_to_volume(
            50,
            hardware_ids=[100],
            virtual_guest_ids=[200],
            ip_address_ids=[300],
            subnet_ids=[400])

        self.assertEqual(fixtures.SoftLayer_Network_Storage.
                         removeAccessFromHostList, result)

        self.assert_called_with(
            'SoftLayer_Network_Storage',
            'removeAccessFromHostList',
            identifier=50)

    def test_get_file_volume_access_list(self):
        self.file.get_file_volume_access_list(100)
        self.assert_called_with(
            'SoftLayer_Network_Storage',
            'getObject',
            identifier=100)

    def test_enable_snapshots(self):
        result = self.file.enable_snapshots(12345678, 'WEEKLY', 10,
                                            47, 16, 'FRIDAY')

        self.assertEqual(fixtures.SoftLayer_Network_Storage.enableSnapshots,
                         result)

        self.assert_called_with(
            'SoftLayer_Network_Storage',
            'enableSnapshots',
            identifier=12345678)

    def test_disable_snapshots(self):
        result = self.file.disable_snapshots(12345678, 'HOURLY')

        self.assertEqual(fixtures.SoftLayer_Network_Storage.disableSnapshots,
                         result)
        self.assert_called_with(
            'SoftLayer_Network_Storage',
            'disableSnapshots',
            identifier=12345678)

    def test_snapshot_restore(self):
        result = self.file.restore_from_snapshot(12345678, 87654321)

        self.assertEqual(
            fixtures.SoftLayer_Network_Storage.restoreFromSnapshot,
            result)
        self.assert_called_with(
            'SoftLayer_Network_Storage',
            'restoreFromSnapshot',
            identifier=12345678)

    def test_get_file_volume_details(self):
        result = self.file.get_file_volume_details(100)

        self.assertEqual(fixtures.SoftLayer_Network_Storage.getObject, result)

        expected_mask = 'id,'\
                        'username,'\
                        'password,'\
                        'capacityGb,'\
                        'bytesUsed,'\
                        'snapshotCapacityGb,'\
                        'parentVolume.snapshotSizeBytes,'\
                        'storageType.keyName,'\
                        'serviceResource.datacenter[name],'\
                        'serviceResourceBackendIpAddress,'\
                        'fileNetworkMountAddress,'\
                        'storageTierLevel,'\
                        'iops,'\
                        'lunId,'\
                        'originalVolumeName,'\
                        'originalSnapshotName,'\
                        'originalVolumeSize,'\
                        'activeTransactionCount,'\
                        'activeTransactions.transactionStatus[friendlyName],'\
                        'replicationPartnerCount,'\
                        'replicationStatus,'\
                        'replicationPartners[id,username,'\
                        'serviceResourceBackendIpAddress,'\
                        'serviceResource[datacenter[name]],'\
                        'replicationSchedule[type[keyname]]]'

        self.assert_called_with(
            'SoftLayer_Network_Storage',
            'getObject',
            identifier=100,
            mask='mask[%s]' % expected_mask)

    def test_get_file_volume_snapshot_list(self):
        result = self.file.get_file_volume_snapshot_list(100)

        self.assertEqual(fixtures.SoftLayer_Network_Storage.getSnapshots,
                         result)

        self.assert_called_with(
            'SoftLayer_Network_Storage',
            'getSnapshots',
            identifier=100)

    def test_create_snapshot(self):
        result = self.file.create_snapshot(123, 'hello world')

        self.assertEqual(fixtures.SoftLayer_Network_Storage.createSnapshot,
                         result)

        self.assert_called_with(
            'SoftLayer_Network_Storage',
            'createSnapshot',
            identifier=123)

    def test_cancel_snapshot_immediately(self):
        self.file.cancel_snapshot_space(1234, immediate=True)

        self.assert_called_with(
            'SoftLayer_Billing_Item',
            'cancelItem',
            args=(True, True, 'No longer needed'),
            identifier=123,
        )

    def test_replicant_failover(self):
        result = self.file.failover_to_replicant(1234, 5678, immediate=True)

        self.assertEqual(
            fixtures.SoftLayer_Network_Storage.failoverToReplicant, result)
        self.assert_called_with(
            'SoftLayer_Network_Storage',
            'failoverToReplicant',
            args=(5678, True),
            identifier=1234,
        )

    def test_replicant_failback(self):
        result = self.file.failback_from_replicant(1234, 5678)

        self.assertEqual(
            fixtures.SoftLayer_Network_Storage.failbackFromReplicant, result)
        self.assert_called_with(
            'SoftLayer_Network_Storage',
            'failbackFromReplicant',
            args=(5678,),
            identifier=1234,
        )

    def test_get_replication_partners(self):
        self.file.get_replication_partners(1234)

        self.assert_called_with(
            'SoftLayer_Network_Storage',
            'getReplicationPartners',
            identifier=1234,
        )

    def test_get_replication_locations(self):
        self.file.get_replication_locations(1234)

        self.assert_called_with(
            'SoftLayer_Network_Storage',
            'getValidReplicationTargetDatacenterLocations',
            identifier=1234,
        )

    def test_delete_snapshot(self):
        result = self.file.delete_snapshot(100)

        self.assertEqual(fixtures.SoftLayer_Network_Storage.deleteObject,
                         result)

        self.assert_called_with(
            'SoftLayer_Network_Storage',
            'deleteObject',
            identifier=100)

    def test_order_file_volume_invalid_location(self):
        mock = self.set_mock('SoftLayer_Location_Datacenter', 'getDatacenters')
        mock.return_value = []

        exception = self.assertRaises(
            exceptions.SoftLayerError,
            self.file.order_file_volume,
            "performance_storage_nfs",
            "dal05",
            100,
            None,
            iops=100,
        )

        self.assertEqual(str(exception), "Invalid datacenter name "
                                         "specified. Please provide the "
                                         "lower case short name "
                                         "(e.g.: dal09)")

    def test_order_file_volume_no_package(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = []

        self.assertRaises(
            ValueError,
            self.file.order_file_volume,
            "performance_storage_nfs",
            "dal05",
            40,
            None,
            iops=100,
        )

    def test_order_file_volume_too_many_packages(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [{}, {}]

        self.assertRaises(
            ValueError,
            self.file.order_file_volume,
            "performance_storage_nfs",
            "dal05",
            40,
            None,
            iops=100,
        )

    def test_order_file_volume_invalid_storage_type(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [{}]

        exception = self.assertRaises(
            exceptions.SoftLayerError,
            self.file.order_file_volume,
            "something_completely_different",
            "dal05",
            100,
            None,
            iops=100,
        )
        self.assertEqual(str(exception), "File volume storage_type must be "
                                         "either Performance or Endurance")

    def test_order_file_volume_os_type_provided(self):
        exception = self.assertRaises(
            exceptions.SoftLayerError,
            self.file.order_file_volume,
            "performance_storage_nfs",
            "dal05",
            100,
            "LINUX",
            iops=100,
        )
        self.assertEqual(str(exception), "OS type is not used on file "
                                         "storage orders")

    def test_order_file_volume_performance(self):
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
                        'categoryCode': 'performance_storage_nfs',
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

        result = self.file.order_file_volume(
            "performance_storage_nfs",
            "dal05",
            100,
            None,
            iops=100,
            )

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

    def test_list_file_volumes(self):
        result = self.file.list_file_volumes()

        self.assertEqual(fixtures.SoftLayer_Account.getNasNetworkStorage,
                         result)

        self.assert_called_with('SoftLayer_Account', 'getNasNetworkStorage')

    def test_order_file_volume_endurance(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [{
            'id': 1,
            'name': 'Endurance',
            'items': [{
                'capacity': '1',
                'prices': [{
                    'id': 1,
                    'locationGroupId': '',
                    'categories': [{
                        'categoryCode': 'storage_file',
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

        result = self.file.order_file_volume(
            "storage_service_enterprise",
            "dal05",
            100,
            None,
            tier_level=0.25,
            )

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

    def test_order_file_volume_endurance_with_snapshot(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [{
            'id': 1,
            'name': 'Endurance',
            'items': [{
                'capacity': '1',
                'prices': [{
                    'id': 1,
                    'locationGroupId': '',
                    'categories': [{
                        'categoryCode': 'storage_file',
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
            }, {
                'capacity': '10',
                'prices': [{
                    'id': 5,
                    'locationGroupId': '',
                    'categories': [{
                        'categoryCode': 'storage_snapshot_space',
                    }],
                    'capacityRestrictionMinimum': '100',
                    'capacityRestrictionMaximum': '100',
                }],
            }],
        }]

        result = self.file.order_file_volume(
            "storage_service_enterprise",
            "dal05",
            100,
            None,
            tier_level=0.25,
            snapshot_size=10,
            )

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

    def test_order_snapshot_space_no_package(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = []

        self.assertRaises(
            ValueError,
            self.file.order_snapshot_space,
            100,
            5,
            None,
            False,
        )

    def test_order_snapshot_space_too_many_packages(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [{}, {}]

        self.assertRaises(
            ValueError,
            self.file.order_snapshot_space,
            100,
            5,
            None,
            False,
        )

    def test_order_snapshot_space_invalid_category(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [{
            'id': 240,
            'name': 'Endurance',
            'items': [{
                'capacity': '0',
            }, {
                'capacity': '5',
                'prices': [{
                    'locationGroupId': '530',
                    }],
            }, {
                'capacity': '5',
                'prices': [{
                    'locationGroupId': '',
                    'categories': [{
                        'categoryCode': 'storage_file',
                    }],
                }],
            }, {
                'capacity': '5',
                'prices': [{
                    'locationGroupId': '',
                    'categories': [{
                        'categoryCode': 'storage_snapshot_space',
                    }],
                    'capacityRestrictionMinimum': '300',
                }],
            }, {
                'capacity': '5',
                'prices': [{
                    'locationGroupId': '',
                    'categories': [{
                        'categoryCode': 'storage_snapshot_space',
                    }],
                    'capacityRestrictionMinimum': '100',
                    'capacityRestrictionMaximum': '100',
                }],
            }, {
                'capacity': '5',
                'prices': [{
                    'id': 46130,
                    'locationGroupId': '',
                    'categories': [{
                        'categoryCode': 'storage_snapshot_space',
                    }],
                    'capacityRestrictionMinimum': '200',
                    'capacityRestrictionMaximum': '200',
                }],
            }],
        }]

        billing_item_mock = self.set_mock('SoftLayer_Network_Storage',
                                          'getObject')
        billing_item_mock.return_value = {
            'billingItem': {
                'categoryCode': 'not_storage_service_enterprise'
            }
        }

        exception = self.assertRaises(
            exceptions.SoftLayerError,
            self.file.order_snapshot_space,
            100,
            5,
            None,
            False,
        )
        self.assertEqual(str(exception), "File volume storage_type must be "
                                         "Endurance")

    def test_order_snapshot_space(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [{
            'id': 240,
            'name': 'Endurance',
            'items': [{
                'capacity': '0',
            }, {
                'capacity': '5',
                'prices': [{
                    'locationGroupId': '530',
                    }],
            }, {
                'capacity': '5',
                'prices': [{
                    'locationGroupId': '',
                    'categories': [{
                        'categoryCode': 'storage_file',
                    }],
                }],
            }, {
                'capacity': '5',
                'prices': [{
                    'locationGroupId': '',
                    'categories': [{
                        'categoryCode': 'storage_snapshot_space',
                    }],
                    'capacityRestrictionMinimum': '300',
                }],
            }, {
                'capacity': '5',
                'prices': [{
                    'locationGroupId': '',
                    'categories': [{
                        'categoryCode': 'storage_snapshot_space',
                    }],
                    'capacityRestrictionMinimum': '100',
                    'capacityRestrictionMaximum': '100',
                }],
            }, {
                'capacity': '5',
                'prices': [{
                    'id': 46130,
                    'locationGroupId': '',
                    'categories': [{
                        'categoryCode': 'storage_snapshot_space',
                    }],
                    'capacityRestrictionMinimum': '200',
                    'capacityRestrictionMaximum': '200',
                }],
            }],
        }]

        result = self.file.order_snapshot_space(
            100,
            5,
            None,
            False,
            )

        self.assertEqual(
            result,
            {
                'orderId': 1234,
                'orderDate': '2013-08-01 15:23:45',
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

    def test_order_file_replicant_invalid_location(self):
        self.assertRaises(
            exceptions.SoftLayerError,
            self.file.order_replicant_volume,
            100,
            'WEEKLY',
            'moon_center',
        )

    def test_order_file_replicant_invalid_storage_type(self):
        mock = self.set_mock('SoftLayer_Network_Storage', 'getObject')

        mock.return_value = {
            'capacityGb': 20,
            'billingItem': {
                'categoryCode': 'not_the_storage_you_are_looking_for'
            }
        }

        self.assertRaises(
            exceptions.SoftLayerError,
            self.file.order_replicant_volume,
            100,
            'WEEKLY',
            'dal05',
        )

    def test_order_file_replicant_no_snapshot_space(self):
        mock = self.set_mock('SoftLayer_Network_Storage', 'getObject')

        mock.return_value = {
            'capacityGb': 20,
            'billingItem': {
                'categoryCode': 'storage_service_enterprise'
            }
        }

        self.assertRaises(
            exceptions.SoftLayerError,
            self.file.order_replicant_volume,
            100,
            'WEEKLY',
            'dal05',
        )

    def test_order_file_replicant_primary_volume_cancelled(self):
        mock = self.set_mock('SoftLayer_Network_Storage', 'getObject')

        mock.return_value = {
            'capacityGb': 20,
            'snapshotCapacityGb': '10',
            'schedules': [{
                'id': 7770,
                'type': {'keyname': 'SNAPSHOT_WEEKLY'}
            }],
            'billingItem': {
                'categoryCode': 'storage_service_enterprise',
                'cancellationDate': '2016-09-04T22:00:00-07:00'
            }
        }

        self.assertRaises(
            exceptions.SoftLayerError,
            self.file.order_replicant_volume,
            100,
            'WEEKLY',
            'dal05',
        )

    def test_order_file_replicant_snapshot_space_cancelled(self):
        mock = self.set_mock('SoftLayer_Network_Storage', 'getObject')

        mock.return_value = {
            'capacityGb': 20,
            'snapshotCapacityGb': '10',
            'schedules': [{
                'id': 7770,
                'type': {'keyname': 'SNAPSHOT_WEEKLY'}
            }],
            'billingItem': {
                'categoryCode': 'storage_service_enterprise',
                'cancellationDate': '',
                'activeChildren': [{
                    'categoryCode': 'storage_snapshot_space',
                    'cancellationDate': '2016-09-04T22:00:00-07:00'
                }]
            }
        }

        self.assertRaises(
            exceptions.SoftLayerError,
            self.file.order_replicant_volume,
            100,
            'WEEKLY',
            'dal05',
        )

    def test_order_file_replicant(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [{
            'id': 240,
            'name': 'Endurance',
            'items': [{
                'capacity': '0',
                'attributes': [{
                    'value': '42',
                }],
                'prices': [{
                    'locationGroupId': '530',
                }],
            }, {
                'capacity': '10',
                'attributes': [{
                    'value': '200',
                }],
                'prices': [{
                    'locationGroupId': '530',
                }, {
                    'locationGroupId': '',
                    'categories': [{
                        'categoryCode': 'storage_service_enterprise',
                    }],
                }, {
                    'locationGroupId': '',
                    'categories': [{
                        'categoryCode': 'storage_tier_level',
                    }],
                }, {
                    'id': 46130,
                    'locationGroupId': '',
                    'categories': [{
                        'categoryCode': 'storage_snapshot_space',
                    }],
                    'capacityRestrictionMinimum': '200',
                    'capacityRestrictionMaximum': '200',
                }],
            }, {
                'capacity': '20',
                'prices': [{
                    'locationGroupId': '530',
                }, {
                    'locationGroupId': '',
                    'categories': [{
                        'categoryCode': 'storage_file',
                    }],
                }, {
                    'locationGroupId': '',
                    'categories': [{
                        'categoryCode': 'storage_service_enterprise',
                    }],
                }, {
                    'locationGroupId': '',
                    'categories': [{
                        'categoryCode': 'performance_storage_space',
                    }],
                    'capacityRestrictionMinimum': '742',
                }, {
                    'locationGroupId': '',
                    'categories': [{
                        'categoryCode': 'performance_storage_space',
                    }],
                    'capacityRestrictionMinimum': '42',
                    'capacityRestrictionMaximum': '42',
                }, {
                    'locationGroupId': '',
                    'categories': [{
                        'categoryCode': 'performance_storage_space',
                    }],
                    'capacityRestrictionMinimum': '200',
                    'capacityRestrictionMaximum': '200',
                }, {
                    'locationGroupId': '',
                    'categories': [{
                        'categoryCode': 'performance_storage_replication',
                    }],
                    'capacityRestrictionMinimum': '742',
                }, {
                    'locationGroupId': '',
                    'categories': [{
                        'categoryCode': 'performance_storage_replication',
                    }],
                    'capacityRestrictionMinimum': '42',
                    'capacityRestrictionMaximum': '42',
                }, {
                    'locationGroupId': '',
                    'categories': [{
                        'categoryCode': 'performance_storage_replication',
                    }],
                    'capacityRestrictionMinimum': '200',
                    'capacityRestrictionMaximum': '200',
                }],
            }],
        }]

        result = self.file.order_replicant_volume(
            100,
            'WEEKLY',
            'dal05',
            )

        self.assertEqual(
            result,
            {
                'orderId': 1234,
                'orderDate': '2013-08-01 15:23:45',
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

    def test_order_file_duplicate_performance_no_duplicate_snapshot(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [fixtures.SoftLayer_Product_Package.SAAS_PACKAGE]

        mock_volume = fixtures.SoftLayer_Network_Storage.DUPLICATABLE_VOLUME
        prev_storage_type_keyname = mock_volume['storageType']['keyName']
        mock_volume['storageType']['keyName'] = 'PERFORMANCE_FILE_STORAGE'
        mock = self.set_mock('SoftLayer_Network_Storage', 'getObject')
        mock.return_value = mock_volume

        result = self.file.order_duplicate_volume(
            102,
            duplicate_snapshot_size=0)

        self.assertEqual(fixtures.SoftLayer_Product_Order.placeOrder, result)

        self.assert_called_with(
            'SoftLayer_Product_Order',
            'placeOrder',
            args=({
                'complexType': 'SoftLayer_Container_Product_Order_'
                               'Network_Storage_AsAService',
                'packageId': 759,
                'prices': [
                    {'id': 189433},
                    {'id': 189453},
                    {'id': 189993},
                    {'id': 190053}
                ],
                'volumeSize': 500,
                'quantity': 1,
                'location': 449500,
                'duplicateOriginVolumeId': 102,
                'iops': 1000
            },))

        mock_volume['storageType']['keyName'] = prev_storage_type_keyname

    def test_order_file_duplicate_performance(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [fixtures.SoftLayer_Product_Package.SAAS_PACKAGE]

        mock_volume = fixtures.SoftLayer_Network_Storage.DUPLICATABLE_VOLUME
        prev_storage_type_keyname = mock_volume['storageType']['keyName']
        mock_volume['storageType']['keyName'] = 'PERFORMANCE_FILE_STORAGE'
        mock = self.set_mock('SoftLayer_Network_Storage', 'getObject')
        mock.return_value = mock_volume

        result = self.file.order_duplicate_volume(
            102,
            origin_snapshot_id=470,
            duplicate_size=1000,
            duplicate_iops=2000,
            duplicate_tier_level=None,
            duplicate_snapshot_size=10
            )

        self.assertEqual(fixtures.SoftLayer_Product_Order.placeOrder, result)

        self.assert_called_with(
            'SoftLayer_Product_Order',
            'placeOrder',
            args=({
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
                'duplicateOriginSnapshotId': 470,
                'iops': 2000
            },))

        mock_volume['storageType']['keyName'] = prev_storage_type_keyname

    def test_order_file_duplicate_endurance_no_duplicate_snapshot(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [fixtures.SoftLayer_Product_Package.SAAS_PACKAGE]

        mock_volume = fixtures.SoftLayer_Network_Storage.DUPLICATABLE_VOLUME
        prev_storage_type_keyname = mock_volume['storageType']['keyName']
        mock_volume['storageType']['keyName'] = 'ENDURANCE_FILE_STORAGE'
        mock = self.set_mock('SoftLayer_Network_Storage', 'getObject')
        mock.return_value = mock_volume

        result = self.file.order_duplicate_volume(
            102,
            duplicate_snapshot_size=0)

        self.assertEqual(fixtures.SoftLayer_Product_Order.placeOrder, result)

        self.assert_called_with(
            'SoftLayer_Product_Order',
            'placeOrder',
            args=({
                'complexType': 'SoftLayer_Container_Product_Order_'
                               'Network_Storage_AsAService',
                'packageId': 759,
                'prices': [
                    {'id': 189433},
                    {'id': 189453},
                    {'id': 193433},
                    {'id': 193373}
                ],
                'volumeSize': 500,
                'quantity': 1,
                'location': 449500,
                'duplicateOriginVolumeId': 102
            },))

        mock_volume['storageType']['keyName'] = prev_storage_type_keyname

    def test_order_file_duplicate_endurance(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [fixtures.SoftLayer_Product_Package.SAAS_PACKAGE]

        mock_volume = fixtures.SoftLayer_Network_Storage.DUPLICATABLE_VOLUME
        prev_storage_type_keyname = mock_volume['storageType']['keyName']
        mock_volume['storageType']['keyName'] = 'ENDURANCE_FILE_STORAGE'
        mock = self.set_mock('SoftLayer_Network_Storage', 'getObject')
        mock.return_value = mock_volume

        result = self.file.order_duplicate_volume(
            102,
            origin_snapshot_id=470,
            duplicate_size=1000,
            duplicate_iops=None,
            duplicate_tier_level=4,
            duplicate_snapshot_size=10
            )

        self.assertEqual(fixtures.SoftLayer_Product_Order.placeOrder, result)

        self.assert_called_with(
            'SoftLayer_Product_Order',
            'placeOrder',
            args=({
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
                'duplicateOriginSnapshotId': 470
            },))

        mock_volume['storageType']['keyName'] = prev_storage_type_keyname
