"""
    SoftLayer.block
    ~~~~~~~~~~~~~~~
    Block Storage Manager

    :license: MIT, see LICENSE for more details.
"""
from SoftLayer import exceptions
from SoftLayer.managers import storage_utils
from SoftLayer import utils

# pylint: disable=too-many-public-methods


class BlockStorageManager(utils.IdentifierMixin, object):
    """Manages SoftLayer Block Storage volumes.

    See product information here: http://www.softlayer.com/block-storage

    :param SoftLayer.API.BaseClient client: the client instance
    """

    def __init__(self, client):
        self.configuration = {}
        self.client = client

    def list_block_volumes(self, datacenter=None, username=None,
                           storage_type=None, **kwargs):
        """Returns a list of block volumes.

        :param datacenter: Datacenter short name (e.g.: dal09)
        :param username: Name of volume.
        :param storage_type: Type of volume: Endurance or Performance
        :param kwargs:
        :return: Returns a list of block volumes.
        """
        if 'mask' not in kwargs:
            items = [
                'id',
                'username',
                'lunId',
                'capacityGb',
                'bytesUsed',
                'serviceResource.datacenter[name]',
                'serviceResourceBackendIpAddress',
                'activeTransactionCount'
            ]
            kwargs['mask'] = ','.join(items)

        _filter = utils.NestedDict(kwargs.get('filter') or {})

        _filter['iscsiNetworkStorage']['serviceResource']['type']['type'] = \
            (utils.query_filter('!~ ISCSI'))

        _filter['iscsiNetworkStorage']['storageType']['keyName'] = (
            utils.query_filter('*BLOCK_STORAGE*'))
        if storage_type:
            _filter['iscsiNetworkStorage']['storageType']['keyName'] = (
                utils.query_filter('%s_BLOCK_STORAGE' % storage_type.upper()))

        if datacenter:
            _filter['iscsiNetworkStorage']['serviceResource']['datacenter'][
                'name'] = (utils.query_filter(datacenter))

        if username:
            _filter['iscsiNetworkStorage']['username'] = \
                (utils.query_filter(username))

        kwargs['filter'] = _filter.to_dict()
        return self.client.call('Account', 'getIscsiNetworkStorage', **kwargs)

    def get_block_volume_details(self, volume_id, **kwargs):
        """Returns details about the specified volume.

        :param volume_id: ID of volume.
        :param kwargs:
        :return: Returns details about the specified volume.
        """

        if 'mask' not in kwargs:
            items = [
                'id',
                'username',
                'password',
                'capacityGb',
                'snapshotCapacityGb',
                'parentVolume.snapshotSizeBytes',
                'storageType.keyName',
                'serviceResource.datacenter[name]',
                'serviceResourceBackendIpAddress',
                'storageTierLevel',
                'iops',
                'lunId',
                'originalVolumeName',
                'originalSnapshotName',
                'originalVolumeSize',
                'activeTransactionCount',
                'activeTransactions.transactionStatus[friendlyName]',
                'replicationPartnerCount',
                'replicationStatus',
                'replicationPartners[id,username,'
                'serviceResourceBackendIpAddress,'
                'serviceResource[datacenter[name]],'
                'replicationSchedule[type[keyname]]]',
            ]
            kwargs['mask'] = ','.join(items)
        return self.client.call('Network_Storage', 'getObject',
                                id=volume_id, **kwargs)

    def get_block_volume_access_list(self, volume_id, **kwargs):
        """Returns a list of authorized hosts for a specified volume.

        :param volume_id: ID of volume.
        :param kwargs:
        :return: Returns a list of authorized hosts for a specified volume.
        """
        if 'mask' not in kwargs:
            items = [
                'id',
                'allowedVirtualGuests[allowedHost[credential]]',
                'allowedHardware[allowedHost[credential]]',
                'allowedSubnets[allowedHost[credential]]',
                'allowedIpAddresses[allowedHost[credential]]',
            ]
            kwargs['mask'] = ','.join(items)
        return self.client.call('Network_Storage', 'getObject',
                                id=volume_id, **kwargs)

    def get_block_volume_snapshot_list(self, volume_id, **kwargs):
        """Returns a list of snapshots for the specified volume.

        :param volume_id: ID of volume.
        :param kwargs:
        :return: Returns a list of snapshots for the specified volume.
        """
        if 'mask' not in kwargs:
            items = [
                'id',
                'notes',
                'snapshotSizeBytes',
                'storageType[keyName]',
                'snapshotCreationTimestamp',
                'hourlySchedule',
                'dailySchedule',
                'weeklySchedule'
                ]

            kwargs['mask'] = ','.join(items)

        return self.client.call('Network_Storage', 'getSnapshots',
                                id=volume_id, **kwargs)

    def authorize_host_to_volume(self, volume_id,
                                 hardware_ids=None,
                                 virtual_guest_ids=None,
                                 ip_address_ids=None,
                                 **kwargs):
        """Authorizes hosts to Block Storage Volumes

        :param volume_id: The Block volume to authorize hosts to
        :param hardware_ids: A List of SoftLayer_Hardware ids
        :param virtual_guest_ids: A List of SoftLayer_Virtual_Guest ids
        :param ip_address_ids: A List of SoftLayer_Network_Subnet_IpAddress ids
        :return: Returns an array of
                SoftLayer_Network_Storage_Allowed_Host objects
                which now have access to the given Block volume
        """
        host_templates = []
        storage_utils.populate_host_templates(host_templates,
                                              hardware_ids,
                                              virtual_guest_ids,
                                              ip_address_ids,
                                              None)

        return self.client.call('Network_Storage', 'allowAccessFromHostList',
                                host_templates, id=volume_id, **kwargs)

    def deauthorize_host_to_volume(self, volume_id,
                                   hardware_ids=None,
                                   virtual_guest_ids=None,
                                   ip_address_ids=None,
                                   **kwargs):
        """Revokes authorization of hosts to Block Storage Volumes

        :param volume_id: The Block volume to deauthorize hosts to
        :param hardware_ids: A List of SoftLayer_Hardware ids
        :param virtual_guest_ids: A List of SoftLayer_Virtual_Guest ids
        :param ip_address_ids: A List of SoftLayer_Network_Subnet_IpAddress ids
        :return: Returns an array of
                SoftLayer_Network_Storage_Allowed_Host objects
                which have access to the given Block volume
        """
        host_templates = []
        storage_utils.populate_host_templates(host_templates,
                                              hardware_ids,
                                              virtual_guest_ids,
                                              ip_address_ids,
                                              None)

        return self.client.call('Network_Storage', 'removeAccessFromHostList',
                                host_templates, id=volume_id, **kwargs)

    def get_replication_partners(self, volume_id):
        """Acquires list of replicant volumes pertaining to the given volume.

        :param volume_id: The ID of the primary volume to be replicated
        :return: Returns an array of SoftLayer_Location objects
        """
        return self.client.call('Network_Storage',
                                'getReplicationPartners',
                                id=volume_id)

    def get_replication_locations(self, volume_id):
        """Acquires list of the datacenters to which a volume can be replicated.

        :param volume_id: The ID of the primary volume to be replicated
        :return: Returns an array of SoftLayer_Network_Storage objects
        """
        return self.client.call('Network_Storage',
                                'getValidReplicationTargetDatacenterLocations',
                                id=volume_id)

    def order_replicant_volume(self, volume_id, snapshot_schedule,
                               location, tier=None, os_type=None):
        """Places an order for a replicant block volume.

        :param volume_id: The ID of the primary volume to be replicated
        :param snapshot_schedule: The primary volume's snapshot
                                  schedule to use for replication
        :param location: The location for the ordered replicant volume
        :param tier: The tier (IOPS per GB) of the primary volume
        :param os_type: The OS type of the primary volume
        :return: Returns a SoftLayer_Container_Product_Order_Receipt
        """

        block_mask = 'billingItem[activeChildren],storageTierLevel,'\
                     'osType,snapshotCapacityGb,schedules,'\
                     'hourlySchedule,dailySchedule,weeklySchedule'
        block_volume = self.get_block_volume_details(volume_id,
                                                     mask=block_mask)

        if os_type is None:
            if isinstance(utils.lookup(block_volume, 'osType', 'keyName'),
                          str):
                os_type = block_volume['osType']['keyName']
            else:
                raise exceptions.SoftLayerError(
                    "Cannot find primary volume's os-type "
                    "automatically; must specify manually")

        order = storage_utils.prepare_replicant_order_object(
            self, volume_id, snapshot_schedule, location, tier,
            block_volume, 'block'
        )

        order['osFormatType'] = {'keyName': os_type}

        return self.client.call('Product_Order', 'placeOrder', order)

    def order_duplicate_volume(self, origin_volume_id, origin_snapshot_id=None,
                               duplicate_size=None, duplicate_iops=None,
                               duplicate_tier_level=None,
                               duplicate_snapshot_size=None):
        """Places an order for a duplicate block volume.

        :param origin_volume_id: The ID of the origin volume to be duplicated
        :param origin_snapshot_id: Origin snapshot ID to use for duplication
        :param duplicate_size: Size/capacity for the duplicate volume
        :param duplicate_iops: The IOPS per GB for the duplicate volume
        :param duplicate_tier_level: Tier level for the duplicate volume
        :param duplicate_snapshot_size: Snapshot space size for the duplicate
        :return: Returns a SoftLayer_Container_Product_Order_Receipt
        """

        block_mask = 'id,billingItem[location],snapshotCapacityGb,'\
                     'storageType[keyName],capacityGb,originalVolumeSize,'\
                     'provisionedIops,storageTierLevel,osType[keyName]'
        origin_volume = self.get_block_volume_details(origin_volume_id,
                                                      mask=block_mask)

        if isinstance(utils.lookup(origin_volume, 'osType', 'keyName'), str):
            os_type = origin_volume['osType']['keyName']
        else:
            raise exceptions.SoftLayerError(
                "Cannot find origin volume's os-type")

        order = storage_utils.prepare_duplicate_order_object(
            self, origin_volume, duplicate_iops, duplicate_tier_level,
            duplicate_size, duplicate_snapshot_size, 'block'
        )

        order['osFormatType'] = {'keyName': os_type}

        if origin_snapshot_id is not None:
            order['duplicateOriginSnapshotId'] = origin_snapshot_id

        return self.client.call('Product_Order', 'placeOrder', order)

    def delete_snapshot(self, snapshot_id):
        """Deletes the specified snapshot object.

        :param snapshot_id: The ID of the snapshot object to delete.
        """
        return self.client.call('Network_Storage', 'deleteObject',
                                id=snapshot_id)

    def order_block_volume(self, storage_type, location, size, os_type,
                           iops=None, tier_level=None, snapshot_size=None):
        """Places an order for a block volume.

        :param storage_type: "performance_storage_iscsi" (performance)
                             or "storage_service_enterprise" (endurance)
        :param location: Datacenter in which to order iSCSI volume
        :param size: Size of the desired volume, in GB
        :param os_type: OS Type to use for volume alignment, see help for list
        :param iops: Number of IOPs for a "Performance" order
        :param tier_level: Tier level to use for an "Endurance" order
        :param snapshot_size: The size of optional snapshot space,
        if snapshot space should also be ordered (None if not ordered)
        """

        try:
            location_id = storage_utils.get_location_id(self, location)
        except ValueError:
            raise exceptions.SoftLayerError(
                "Invalid datacenter name specified. "
                "Please provide the lower case short name (e.g.: dal09)")

        base_type_name = 'SoftLayer_Container_Product_Order_Network_'
        package = storage_utils.get_package(self, storage_type)
        if storage_type == 'performance_storage_iscsi':
            complex_type = base_type_name + 'PerformanceStorage_Iscsi'
            prices = [
                storage_utils.find_performance_price(
                    package,
                    'performance_storage_iscsi'
                    ),
                storage_utils.find_performance_space_price(package, size),
                storage_utils.find_performance_iops_price(package, size, iops),
            ]
        elif storage_type == 'storage_service_enterprise':
            complex_type = base_type_name + 'Storage_Enterprise'
            prices = [
                storage_utils.find_endurance_price(package, 'storage_block'),
                storage_utils.find_endurance_price(
                    package,
                    'storage_service_enterprise'
                    ),
                storage_utils.find_endurance_space_price(
                    package,
                    size,
                    tier_level
                    ),
                storage_utils.find_endurance_tier_price(package, tier_level),
            ]
            if snapshot_size is not None:
                prices.append(storage_utils.find_snapshot_space_price(
                    package, snapshot_size, tier_level))
        else:
            raise exceptions.SoftLayerError(
                "Block volume storage_type must be either "
                "Performance or Endurance")

        order = {
            'complexType': complex_type,
            'packageId': package['id'],
            'osFormatType': {'keyName': os_type},
            'prices': prices,
            'quantity': 1,
            'location': location_id,
        }

        return self.client.call('Product_Order', 'placeOrder', order)

    def create_snapshot(self, volume_id, notes='', **kwargs):
        """Creates a snapshot on the given block volume.

        :param integer volume_id: The id of the volume
        :param string notes: The notes or "name" to assign the snapshot
        :return: Returns the id of the new snapshot
        """

        return self.client.call('Network_Storage', 'createSnapshot',
                                notes, id=volume_id, **kwargs)

    def order_snapshot_space(self, volume_id, capacity, tier,
                             upgrade, **kwargs):
        """Orders snapshot space for the given block volume.

        :param integer volume_id: The id of the volume
        :param integer capacity: The capacity to order, in GB
        :param float tier: The tier level of the block volume, in IOPS per GB
        :param boolean upgrade: Flag to indicate if this order is an upgrade
        :return: Returns a SoftLayer_Container_Product_Order_Receipt
        """
        package = storage_utils.get_package(self, 'storage_service_enterprise')
        block_mask = 'serviceResource.datacenter[id],'\
            'storageTierLevel,billingItem'
        block_volume = self.get_block_volume_details(volume_id,
                                                     mask=block_mask,
                                                     **kwargs)

        storage_type = block_volume['billingItem']['categoryCode']
        if storage_type != 'storage_service_enterprise':
            raise exceptions.SoftLayerError(
                "Block volume storage_type must be Endurance")

        if tier is None:
            tier = storage_utils.find_endurance_tier_iops_per_gb(block_volume)
        prices = [storage_utils.find_snapshot_space_price(
            package, capacity, tier)]

        if upgrade:
            complex_type = 'SoftLayer_Container_Product_Order_'\
                           'Network_Storage_Enterprise_SnapshotSpace_Upgrade'
        else:
            complex_type = 'SoftLayer_Container_Product_Order_'\
                           'Network_Storage_Enterprise_SnapshotSpace'

        snapshot_space_order = {
            'complexType': complex_type,
            'packageId': package['id'],
            'prices': prices,
            'quantity': 1,
            'location': block_volume['serviceResource']['datacenter']['id'],
            'volumeId': volume_id,
        }

        return self.client.call('Product_Order', 'placeOrder',
                                snapshot_space_order)

    def cancel_snapshot_space(self, volume_id,
                              reason='No longer needed',
                              immediate=False):
        """Cancels snapshot space for a given volume.

        :param integer volume_id: The volume ID
        :param string reason: The reason for cancellation
        :param boolean immediate_flag: Cancel immediately or
        on anniversary date
        """

        block_volume = self.get_block_volume_details(
            volume_id,
            mask='mask[id,billingItem[activeChildren]]')

        if 'activeChildren' not in block_volume['billingItem']:
            raise exceptions.SoftLayerError(
                'No snapshot space found to cancel')

        children_array = block_volume['billingItem']['activeChildren']
        billing_item_id = None

        for child in children_array:
            if child['categoryCode'] == 'storage_snapshot_space':
                billing_item_id = child['id']
                break

        if not billing_item_id:
            raise exceptions.SoftLayerError(
                'No snapshot space found to cancel')

        return self.client['Billing_Item'].cancelItem(
            immediate,
            True,
            reason,
            id=billing_item_id)

    def enable_snapshots(self, volume_id, schedule_type, retention_count,
                         minute, hour, day_of_week, **kwargs):
        """Enables snapshots for a specific block volume at a given schedule

        :param integer volume_id: The id of the volume
        :param string schedule_type: 'HOURLY'|'DAILY'|'WEEKLY'
        :param integer retention_count: Number of snapshots to be kept
        :param integer minute: Minute when to take snapshot
        :param integer hour: Hour when to take snapshot
        :param string day_of_week: Day when to take snapshot
        :return: Returns whether successfully scheduled or not
        """

        return self.client.call('Network_Storage', 'enableSnapshots',
                                schedule_type,
                                retention_count,
                                minute,
                                hour,
                                day_of_week,
                                id=volume_id,
                                **kwargs)

    def disable_snapshots(self, volume_id, schedule_type):
        """Disables snapshots for a specific block volume at a given schedule

        :param integer volume_id: The id of the volume
        :param string schedule_type: 'HOURLY'|'DAILY'|'WEEKLY'
        :return: Returns whether successfully disabled or not
        """

        return self.client.call('Network_Storage', 'disableSnapshots',
                                schedule_type, id=volume_id)

    def restore_from_snapshot(self, volume_id, snapshot_id):
        """Restores a specific volume from a snapshot

        :param integer volume_id: The id of the volume
        :param integer snapshot_id: The id of the restore point
        :return: Returns whether succesfully restored or not
        """

        return self.client.call('Network_Storage', 'restoreFromSnapshot',
                                snapshot_id, id=volume_id)

    def cancel_block_volume(self, volume_id,
                            reason='No longer needed',
                            immediate=False):
        """Cancels the given block storage volume.

        :param integer volume_id: The volume ID
        :param string reason: The reason for cancellation
        :param boolean immediate_flag: Cancel immediately or
        on anniversary date
        """
        block_volume = self.get_block_volume_details(
            volume_id,
            mask='mask[id,billingItem[id]]')
        billing_item_id = block_volume['billingItem']['id']

        return self.client['Billing_Item'].cancelItem(
            immediate,
            True,
            reason,
            id=billing_item_id)

    def failover_to_replicant(self, volume_id, replicant_id, immediate=False):
        """Failover to a volume replicant.

        :param integer volume_id: The id of the volume
        :param integer replicant_id: ID of replicant to failover to
        :param boolean immediate: Flag indicating if failover is immediate
        :return: Returns whether failover was successful or not
        """

        return self.client.call('Network_Storage', 'failoverToReplicant',
                                replicant_id, immediate, id=volume_id)

    def failback_from_replicant(self, volume_id, replicant_id):
        """Failback from a volume replicant.

        :param integer volume_id: The id of the volume
        :param integer: ID of replicant to failback from
        :return: Returns whether failback was successful or not
        """

        return self.client.call('Network_Storage', 'failbackFromReplicant',
                                replicant_id, id=volume_id)

    def set_credential_password(self, access_id, password):
        """Sets the password for an access host

        :param integer access_id: id of the access host
        :param string password: password to  set
        """

        return self.client.call('Network_Storage_Allowed_Host', 'setCredentialPassword',
                                password, id=access_id)
