"""
    SoftLayer.tests.managers.block_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""

import copy
import SoftLayer
from SoftLayer import exceptions
from SoftLayer import fixtures
from SoftLayer import testing


class BlockTests(testing.TestCase):
    def set_up(self):
        self.block = SoftLayer.BlockStorageManager(self.client)

    def test_cancel_block_volume_immediately(self):
        self.block.cancel_block_volume(123, immediate=True)

        self.assert_called_with(
            'SoftLayer_Billing_Item',
            'cancelItem',
            args=(True, True, 'No longer needed'),
            identifier=449,
        )

    def test_cancel_block_volume_immediately_hourly_billing(self):
        mock = self.set_mock('SoftLayer_Network_Storage', 'getObject')
        mock.return_value = {
            'billingItem': {'hourlyFlag': True, 'id': 449},
        }

        self.block.cancel_block_volume(123, immediate=False)

        self.assert_called_with(
            'SoftLayer_Billing_Item',
            'cancelItem',
            args=(True, True, 'No longer needed'),
            identifier=449,
        )

    def test_cancel_block_volume_exception_billing_item_not_found(self):
        mock = self.set_mock('SoftLayer_Network_Storage', 'getObject')
        mock.return_value = {
            'capacityGb': 20,
            'createDate': '2017-06-20T14:24:21-06:00',
            'nasType': 'ISCSI',
            'storageTypeId': '7',
            'serviceResourceName': 'PerfStor Aggr aggr_staasdal0601_pc01'
        }
        exception = self.assertRaises(
            exceptions.SoftLayerError,
            self.block.cancel_block_volume,
            12345,
            immediate=True
        )
        self.assertEqual(
            'Block Storage was already cancelled',
            str(exception)
        )

    def test_cancel_block_volume_billing_item_found(self):
        mock = self.set_mock('SoftLayer_Network_Storage', 'getObject')
        mock.return_value = {
            'capacityGb': 20,
            'createDate': '2017-06-20T14:24:21-06:00',
            'nasType': 'ISCSI',
            'storageTypeId': '7',
            'serviceResourceName': 'PerfStor Aggr aggr_staasdal0601_pc01',
            'billingItem': {'hourlyFlag': True, 'id': 449},
        }
        self.block.cancel_block_volume(123, immediate=False)

        self.assert_called_with(
            'SoftLayer_Billing_Item',
            'cancelItem',
            args=(True, True, 'No longer needed'),
            identifier=449,
        )

    def test_get_block_volume_details(self):
        result = self.block.get_block_volume_details(100)

        self.assertEqual(fixtures.SoftLayer_Network_Storage.getObject, result)

        expected_mask = 'id,' \
                        'username,' \
                        'password,' \
                        'capacityGb,' \
                        'snapshotCapacityGb,' \
                        'parentVolume.snapshotSizeBytes,' \
                        'storageType.keyName,' \
                        'serviceResource.datacenter[name],' \
                        'serviceResourceBackendIpAddress,' \
                        'storageTierLevel,' \
                        'provisionedIops,' \
                        'lunId,' \
                        'originalVolumeName,' \
                        'originalSnapshotName,' \
                        'originalVolumeSize,' \
                        'activeTransactionCount,' \
                        'activeTransactions.transactionStatus[friendlyName],' \
                        'replicationPartnerCount,' \
                        'replicationStatus,' \
                        'replicationPartners[id,username,' \
                        'serviceResourceBackendIpAddress,' \
                        'serviceResource[datacenter[name]],' \
                        'replicationSchedule[type[keyname]]]'

        self.assert_called_with(
            'SoftLayer_Network_Storage',
            'getObject',
            identifier=100,
            mask='mask[%s]' % expected_mask
        )

    def test_list_block_volumes(self):
        result = self.block.list_block_volumes()

        self.assertEqual(fixtures.SoftLayer_Account.getIscsiNetworkStorage,
                         result)

        expected_filter = {
            'iscsiNetworkStorage': {
                'storageType': {
                    'keyName': {'operation': '*= BLOCK_STORAGE'}
                },
                'serviceResource': {
                    'type': {
                        'type': {'operation': '!~ ISCSI'}
                    }
                }
            }
        }

        expected_mask = 'id,' \
                        'username,' \
                        'lunId,' \
                        'capacityGb,' \
                        'bytesUsed,' \
                        'serviceResource.datacenter[name],' \
                        'serviceResourceBackendIpAddress,' \
                        'activeTransactionCount,' \
                        'replicationPartnerCount'

        self.assert_called_with(
            'SoftLayer_Account',
            'getIscsiNetworkStorage',
            filter=expected_filter,
            mask='mask[%s]' % expected_mask
        )

    def test_list_block_volumes_with_additional_filters(self):
        result = self.block.list_block_volumes(datacenter="dal09",
                                               storage_type="Endurance",
                                               username="username")

        self.assertEqual(fixtures.SoftLayer_Account.getIscsiNetworkStorage,
                         result)

        expected_filter = {
            'iscsiNetworkStorage': {
                'storageType': {
                    'keyName': {'operation': '^= ENDURANCE_BLOCK_STORAGE'}
                },
                'username': {'operation': u'_= username'},
                'serviceResource': {
                    'datacenter': {
                        'name': {'operation': u'_= dal09'}
                    },
                    'type': {
                        'type': {'operation': '!~ ISCSI'}
                    }
                }
            }
        }

        expected_mask = 'id,' \
                        'username,' \
                        'lunId,' \
                        'capacityGb,' \
                        'bytesUsed,' \
                        'serviceResource.datacenter[name],' \
                        'serviceResourceBackendIpAddress,' \
                        'activeTransactionCount,' \
                        'replicationPartnerCount'

        self.assert_called_with(
            'SoftLayer_Account',
            'getIscsiNetworkStorage',
            filter=expected_filter,
            mask='mask[%s]' % expected_mask
        )

    def test_get_block_volume_access_list(self):
        result = self.block.get_block_volume_access_list(100)

        self.assertEqual(fixtures.SoftLayer_Network_Storage.getObject, result)

        self.assert_called_with(
            'SoftLayer_Network_Storage',
            'getObject',
            identifier=100)

    def test_get_block_volume_snapshot_list(self):
        result = self.block.get_block_volume_snapshot_list(100)

        self.assertEqual(fixtures.SoftLayer_Network_Storage.getSnapshots,
                         result)

        self.assert_called_with(
            'SoftLayer_Network_Storage',
            'getSnapshots',
            identifier=100)

    def test_delete_snapshot(self):
        result = self.block.delete_snapshot(100)

        self.assertEqual(fixtures.SoftLayer_Network_Storage.deleteObject,
                         result)

        self.assert_called_with(
            'SoftLayer_Network_Storage',
            'deleteObject',
            identifier=100)

    def test_cancel_snapshot_immediately(self):
        self.block.cancel_snapshot_space(1234, immediate=True)

        self.assert_called_with(
            'SoftLayer_Billing_Item',
            'cancelItem',
            args=(True, True, 'No longer needed'),
            identifier=123,
        )

    def test_cancel_snapshot_hourly_billing_immediate_true(self):
        mock = self.set_mock('SoftLayer_Network_Storage', 'getObject')
        mock.return_value = {
            'billingItem': {
                'activeChildren': [
                    {'categoryCode': 'storage_snapshot_space', 'id': 417}
                ],
                'hourlyFlag': True,
                'id': 449
            },
        }

        self.block.cancel_snapshot_space(1234, immediate=True)

        self.assert_called_with(
            'SoftLayer_Billing_Item',
            'cancelItem',
            args=(True, True, 'No longer needed'),
            identifier=417,
        )

    def test_cancel_snapshot_hourly_billing_immediate_false(self):
        mock = self.set_mock('SoftLayer_Network_Storage', 'getObject')
        mock.return_value = {
            'billingItem': {
                'activeChildren': [
                    {'categoryCode': 'storage_snapshot_space', 'id': 417}
                ],
                'hourlyFlag': True,
                'id': 449
            },
        }

        self.block.cancel_snapshot_space(1234, immediate=False)

        self.assert_called_with(
            'SoftLayer_Billing_Item',
            'cancelItem',
            args=(True, True, 'No longer needed'),
            identifier=417,
        )

    def test_cancel_snapshot_exception_no_billing_item_active_children(self):
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
        exception = self.assertRaises(
            exceptions.SoftLayerError,
            self.block.cancel_snapshot_space,
            12345,
            immediate=True
        )
        self.assertEqual(
            'No snapshot space found to cancel',
            str(exception)
        )

    def test_cancel_snapshot_exception_snapshot_billing_item_not_found(self):
        mock = self.set_mock('SoftLayer_Network_Storage', 'getObject')
        mock.return_value = {
            'capacityGb': 20,
            'snapshotCapacityGb': '10',
            'schedules': [{
                'id': 7770,
                'type': {'keyname': 'SNAPSHOT_WEEKLY'}
            }],
            'billingItem': {
                'activeChildren': []
            }
        }
        exception = self.assertRaises(
            exceptions.SoftLayerError,
            self.block.cancel_snapshot_space,
            12345,
            immediate=True
        )
        self.assertEqual(
            'No snapshot space found to cancel',
            str(exception)
        )

    def test_replicant_failover(self):
        result = self.block.failover_to_replicant(1234, 5678, immediate=True)

        self.assertEqual(
            fixtures.SoftLayer_Network_Storage.failoverToReplicant, result)
        self.assert_called_with(
            'SoftLayer_Network_Storage',
            'failoverToReplicant',
            args=(5678, True),
            identifier=1234,
        )

    def test_replicant_failback(self):
        result = self.block.failback_from_replicant(1234, 5678)

        self.assertEqual(
            fixtures.SoftLayer_Network_Storage.failbackFromReplicant, result)
        self.assert_called_with(
            'SoftLayer_Network_Storage',
            'failbackFromReplicant',
            args=(5678,),
            identifier=1234,
        )

    def test_get_replication_partners(self):
        self.block.get_replication_partners(1234)

        self.assert_called_with(
            'SoftLayer_Network_Storage',
            'getReplicationPartners',
            identifier=1234,
        )

    def test_get_replication_locations(self):
        self.block.get_replication_locations(1234)

        self.assert_called_with(
            'SoftLayer_Network_Storage',
            'getValidReplicationTargetDatacenterLocations',
            identifier=1234,
        )

    def test_order_block_volume_performance(self):
        mock = self.set_mock('SoftLayer_Location_Datacenter', 'getDatacenters')
        mock.return_value = [{'id': 449494, 'name': 'dal09'}]

        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [fixtures.SoftLayer_Product_Package.SAAS_PACKAGE]

        mock_volume = copy.deepcopy(fixtures.SoftLayer_Network_Storage.STAAS_TEST_VOLUME)
        mock_volume['storageType']['keyName'] = 'PERFORMANCE_BLOCK_STORAGE'
        mock = self.set_mock('SoftLayer_Network_Storage', 'getObject')
        mock.return_value = mock_volume

        result = self.block.order_block_volume(
            'performance',
            'dal09',
            1000,
            'LINUX',
            iops=2000,
            service_offering='storage_as_a_service'
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
                    {'id': 189443},
                    {'id': 190113},
                    {'id': 190173}
                ],
                'volumeSize': 1000,
                'quantity': 1,
                'location': 449494,
                'iops': 2000,
                'useHourlyPricing': False,
                'osFormatType': {'keyName': 'LINUX'}
            },)
        )

    def test_order_block_volume_endurance(self):
        mock = self.set_mock('SoftLayer_Location_Datacenter', 'getDatacenters')
        mock.return_value = [{'id': 449494, 'name': 'dal09'}]

        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [fixtures.SoftLayer_Product_Package.SAAS_PACKAGE]

        mock_volume = fixtures.SoftLayer_Network_Storage.STAAS_TEST_VOLUME
        mock = self.set_mock('SoftLayer_Network_Storage', 'getObject')
        mock.return_value = mock_volume

        result = self.block.order_block_volume(
            'endurance',
            'dal09',
            1000,
            'LINUX',
            tier_level=4,
            service_offering='storage_as_a_service'
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
                    {'id': 189443},
                    {'id': 194763},
                    {'id': 194703}
                ],
                'volumeSize': 1000,
                'quantity': 1,
                'location': 449494,
                'useHourlyPricing': False,
                'osFormatType': {'keyName': 'LINUX'}
            },)
        )

    def test_authorize_host_to_volume(self):
        result = self.block.authorize_host_to_volume(
            50,
            hardware_ids=[100],
            virtual_guest_ids=[200],
            ip_address_ids=[300])

        self.assertEqual(fixtures.SoftLayer_Network_Storage.
                         allowAccessFromHostList, result)

        self.assert_called_with(
            'SoftLayer_Network_Storage',
            'allowAccessFromHostList',
            identifier=50)

    def test_deauthorize_host_to_volume(self):
        result = self.block.deauthorize_host_to_volume(
            50,
            hardware_ids=[100],
            virtual_guest_ids=[200],
            ip_address_ids=[300])

        self.assertEqual(fixtures.SoftLayer_Network_Storage.
                         removeAccessFromHostList, result)

        self.assert_called_with(
            'SoftLayer_Network_Storage',
            'removeAccessFromHostList',
            identifier=50)

    def test_create_snapshot(self):
        result = self.block.create_snapshot(123, 'hello world')

        self.assertEqual(fixtures.SoftLayer_Network_Storage.createSnapshot,
                         result)

        self.assert_called_with(
            'SoftLayer_Network_Storage',
            'createSnapshot',
            identifier=123)

    def test_snapshot_restore(self):
        result = self.block.restore_from_snapshot(12345678, 87654321)

        self.assertEqual(
            fixtures.SoftLayer_Network_Storage.restoreFromSnapshot,
            result)
        self.assert_called_with(
            'SoftLayer_Network_Storage',
            'restoreFromSnapshot',
            identifier=12345678)

    def test_enable_snapshots(self):
        result = self.block.enable_snapshots(12345678, 'WEEKLY', 10,
                                             47, 16, 'FRIDAY')

        self.assertEqual(fixtures.SoftLayer_Network_Storage.enableSnapshots,
                         result)

        self.assert_called_with(
            'SoftLayer_Network_Storage',
            'enableSnapshots',
            identifier=12345678)

    def test_disable_snapshots(self):
        result = self.block.disable_snapshots(12345678, 'HOURLY')

        self.assertEqual(fixtures.SoftLayer_Network_Storage.disableSnapshots,
                         result)
        self.assert_called_with(
            'SoftLayer_Network_Storage',
            'disableSnapshots',
            identifier=12345678)

    def test_list_volume_schedules(self):
        result = self.block.list_volume_schedules(12345678)

        self.assertEqual(
            fixtures.SoftLayer_Network_Storage.listVolumeSchedules,
            result)

        expected_mask = 'schedules[type,properties[type]]'

        self.assert_called_with(
            'SoftLayer_Network_Storage',
            'getObject',
            identifier=12345678,
            mask='mask[%s]' % expected_mask
        )

    def test_order_block_snapshot_space_upgrade(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [fixtures.SoftLayer_Product_Package.SAAS_PACKAGE]

        mock_volume = copy.deepcopy(fixtures.SoftLayer_Network_Storage.STAAS_TEST_VOLUME)
        mock_volume['storageType']['keyName'] = 'ENDURANCE_BLOCK_STORAGE'
        mock = self.set_mock('SoftLayer_Network_Storage', 'getObject')
        mock.return_value = mock_volume

        result = self.block.order_snapshot_space(102, 20, None, True)

        self.assertEqual(fixtures.SoftLayer_Product_Order.placeOrder, result)

        self.assert_called_with(
            'SoftLayer_Product_Order',
            'placeOrder',
            args=({
                'complexType': 'SoftLayer_Container_Product_Order_Network_'
                'Storage_Enterprise_SnapshotSpace_Upgrade',
                'packageId': 759,
                'prices': [
                    {'id': 193853}
                ],
                'quantity': 1,
                'location': 449500,
                'volumeId': 102,
                'useHourlyPricing': False
            },)
        )

    def test_order_block_snapshot_space(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [fixtures.SoftLayer_Product_Package.SAAS_PACKAGE]

        mock_volume = fixtures.SoftLayer_Network_Storage.STAAS_TEST_VOLUME
        mock = self.set_mock('SoftLayer_Network_Storage', 'getObject')
        mock.return_value = mock_volume

        result = self.block.order_snapshot_space(102, 10, None, False)

        self.assertEqual(fixtures.SoftLayer_Product_Order.placeOrder, result)

        self.assert_called_with(
            'SoftLayer_Product_Order',
            'placeOrder',
            args=({
                'complexType': 'SoftLayer_Container_Product_Order_Network_'
                'Storage_Enterprise_SnapshotSpace',
                'packageId': 759,
                'prices': [
                    {'id': 193613}
                ],
                'quantity': 1,
                'location': 449500,
                'volumeId': 102,
                'useHourlyPricing': False
            },)
        )

    def test_order_block_replicant_os_type_not_found(self):
        mock_volume = copy.deepcopy(fixtures.SoftLayer_Network_Storage.STAAS_TEST_VOLUME)
        del mock_volume['osType']
        mock = self.set_mock('SoftLayer_Network_Storage', 'getObject')
        mock.return_value = mock_volume

        exception = self.assertRaises(
            exceptions.SoftLayerError,
            self.block.order_replicant_volume,
            102, 'WEEKLY', 'dal09'
        )

        self.assertEqual(
            "Cannot find primary volume's os-type "
            "automatically; must specify manually",
            str(exception)
        )

    def test_order_block_replicant_performance_os_type_given(self):
        mock = self.set_mock('SoftLayer_Location_Datacenter', 'getDatacenters')
        mock.return_value = [{'id': 449494, 'name': 'dal09'}]

        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [fixtures.SoftLayer_Product_Package.SAAS_PACKAGE]

        mock_volume = copy.deepcopy(fixtures.SoftLayer_Network_Storage.STAAS_TEST_VOLUME)
        mock_volume['storageType']['keyName'] = 'PERFORMANCE_BLOCK_STORAGE'
        mock = self.set_mock('SoftLayer_Network_Storage', 'getObject')
        mock.return_value = mock_volume

        result = self.block.order_replicant_volume(
            102,
            'WEEKLY',
            'dal09',
            os_type='XEN'
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
                    {'id': 189443},
                    {'id': 189993},
                    {'id': 190053},
                    {'id': 191193},
                    {'id': 192033}
                ],
                'volumeSize': 500,
                'quantity': 1,
                'location': 449494,
                'iops': 1000,
                'originVolumeId': 102,
                'originVolumeScheduleId': 978,
                'useHourlyPricing': False,
                'osFormatType': {'keyName': 'XEN'}
            },)
        )

    def test_order_block_replicant_endurance(self):
        mock = self.set_mock('SoftLayer_Location_Datacenter', 'getDatacenters')
        mock.return_value = [{'id': 449494, 'name': 'dal09'}]

        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [fixtures.SoftLayer_Product_Package.SAAS_PACKAGE]

        mock_volume = fixtures.SoftLayer_Network_Storage.STAAS_TEST_VOLUME
        mock = self.set_mock('SoftLayer_Network_Storage', 'getObject')
        mock.return_value = mock_volume

        result = self.block.order_replicant_volume(102, 'WEEKLY', 'dal09')

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
                    {'id': 189443},
                    {'id': 193433},
                    {'id': 193373},
                    {'id': 193613},
                    {'id': 194693}
                ],
                'volumeSize': 500,
                'quantity': 1,
                'location': 449494,
                'originVolumeId': 102,
                'originVolumeScheduleId': 978,
                'useHourlyPricing': False,
                'osFormatType': {'keyName': 'LINUX'}
            },)
        )

    def test_order_block_duplicate_origin_os_type_not_found(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [fixtures.SoftLayer_Product_Package.SAAS_PACKAGE]

        mock_volume = copy.deepcopy(fixtures.SoftLayer_Network_Storage.STAAS_TEST_VOLUME)
        del mock_volume['osType']
        mock = self.set_mock('SoftLayer_Network_Storage', 'getObject')
        mock.return_value = mock_volume

        exception = self.assertRaises(
            exceptions.SoftLayerError,
            self.block.order_duplicate_volume,
            102
        )

        self.assertEqual(str(exception),
                         "Cannot find origin volume's os-type")

    def test_order_block_duplicate_performance_no_duplicate_snapshot(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [fixtures.SoftLayer_Product_Package.SAAS_PACKAGE]

        mock_volume = copy.deepcopy(fixtures.SoftLayer_Network_Storage.STAAS_TEST_VOLUME)
        mock_volume['storageType']['keyName'] = 'PERFORMANCE_BLOCK_STORAGE'
        mock = self.set_mock('SoftLayer_Network_Storage', 'getObject')
        mock.return_value = mock_volume

        result = self.block.order_duplicate_volume(
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
                    {'id': 189443},
                    {'id': 189993},
                    {'id': 190053}
                ],
                'volumeSize': 500,
                'quantity': 1,
                'location': 449500,
                'duplicateOriginVolumeId': 102,
                'osFormatType': {'keyName': 'LINUX'},
                'iops': 1000,
                'useHourlyPricing': False
            },))

    def test_order_block_duplicate_performance(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [fixtures.SoftLayer_Product_Package.SAAS_PACKAGE]

        mock_volume = copy.deepcopy(fixtures.SoftLayer_Network_Storage.STAAS_TEST_VOLUME)
        mock_volume['storageType']['keyName'] = 'PERFORMANCE_BLOCK_STORAGE'
        mock = self.set_mock('SoftLayer_Network_Storage', 'getObject')
        mock.return_value = mock_volume

        result = self.block.order_duplicate_volume(
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
                    {'id': 189443},
                    {'id': 190113},
                    {'id': 190173},
                    {'id': 191193}
                ],
                'volumeSize': 1000,
                'quantity': 1,
                'location': 449500,
                'duplicateOriginVolumeId': 102,
                'osFormatType': {'keyName': 'LINUX'},
                'duplicateOriginSnapshotId': 470,
                'iops': 2000,
                'useHourlyPricing': False
            },))

    def test_order_block_duplicate_endurance_no_duplicate_snapshot(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [fixtures.SoftLayer_Product_Package.SAAS_PACKAGE]

        mock_volume = fixtures.SoftLayer_Network_Storage.STAAS_TEST_VOLUME
        mock = self.set_mock('SoftLayer_Network_Storage', 'getObject')
        mock.return_value = mock_volume

        result = self.block.order_duplicate_volume(
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
                    {'id': 189443},
                    {'id': 193433},
                    {'id': 193373}
                ],
                'volumeSize': 500,
                'quantity': 1,
                'location': 449500,
                'duplicateOriginVolumeId': 102,
                'osFormatType': {'keyName': 'LINUX'},
                'useHourlyPricing': False
            },))

    def test_order_block_duplicate_endurance(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [fixtures.SoftLayer_Product_Package.SAAS_PACKAGE]

        mock_volume = fixtures.SoftLayer_Network_Storage.STAAS_TEST_VOLUME
        mock = self.set_mock('SoftLayer_Network_Storage', 'getObject')
        mock.return_value = mock_volume

        result = self.block.order_duplicate_volume(
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
                    {'id': 189443},
                    {'id': 194763},
                    {'id': 194703},
                    {'id': 194943}
                ],
                'volumeSize': 1000,
                'quantity': 1,
                'location': 449500,
                'duplicateOriginVolumeId': 102,
                'osFormatType': {'keyName': 'LINUX'},
                'duplicateOriginSnapshotId': 470,
                'useHourlyPricing': False
            },))

    def test_order_block_modified_performance(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [fixtures.SoftLayer_Product_Package.SAAS_PACKAGE]

        mock_volume = copy.deepcopy(fixtures.SoftLayer_Network_Storage.STAAS_TEST_VOLUME)
        mock_volume['storageType']['keyName'] = 'PERFORMANCE_BLOCK_STORAGE'
        mock = self.set_mock('SoftLayer_Network_Storage', 'getObject')
        mock.return_value = mock_volume

        result = self.block.order_modified_volume(102, new_size=1000, new_iops=2000, new_tier_level=None)

        self.assertEqual(fixtures.SoftLayer_Product_Order.placeOrder, result)
        self.assert_called_with(
            'SoftLayer_Product_Order',
            'placeOrder',
            args=({'complexType': 'SoftLayer_Container_Product_Order_Network_Storage_AsAService_Upgrade',
                   'packageId': 759,
                   'prices': [{'id': 189433}, {'id': 190113}, {'id': 190173}],
                   'volume': {'id': 102},
                   'volumeSize': 1000,
                   'iops': 2000},)
        )

    def test_order_block_modified_endurance(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [fixtures.SoftLayer_Product_Package.SAAS_PACKAGE]

        mock_volume = fixtures.SoftLayer_Network_Storage.STAAS_TEST_VOLUME
        mock = self.set_mock('SoftLayer_Network_Storage', 'getObject')
        mock.return_value = mock_volume

        result = self.block.order_modified_volume(102, new_size=1000, new_iops=None, new_tier_level=4)

        self.assertEqual(fixtures.SoftLayer_Product_Order.placeOrder, result)
        self.assert_called_with(
            'SoftLayer_Product_Order',
            'placeOrder',
            args=({'complexType': 'SoftLayer_Container_Product_Order_Network_Storage_AsAService_Upgrade',
                   'packageId': 759,
                   'prices': [{'id': 189433}, {'id': 194763}, {'id': 194703}],
                   'volume': {'id': 102},
                   'volumeSize': 1000},)
        )

    def test_setCredentialPassword(self):
        mock = self.set_mock('SoftLayer_Network_Storage_Allowed_Host', 'setCredentialPassword')
        mock.return_value = True
        result = self.block.set_credential_password(access_id=102, password='AAAaaa')
        self.assertEqual(True, result)
        self.assert_called_with('SoftLayer_Network_Storage_Allowed_Host', 'setCredentialPassword')
