"""
    SoftLayer.file
    ~~~~~~~~~~~~~~~
    File Storage Manager

    :license: MIT, see LICENSE for more details.
"""
from SoftLayer import exceptions
from SoftLayer.managers import storage_utils
from SoftLayer import utils


class FileStorageManager(utils.IdentifierMixin, object):
    """Manages file Storage volumes."""

    def __init__(self, client):
        self.configuration = {}
        self.client = client

    def list_file_volumes(self, datacenter=None, username=None,
                          storage_type=None, **kwargs):
        """Returns a list of file volumes.

        :param datacenter: Datacenter short name (e.g.: dal09)
        :param username: Name of volume.
        :param storage_type: Type of volume: Endurance or Performance
        :param kwargs:
        :return: Returns a list of file volumes.
        """
        if 'mask' not in kwargs:
            items = [
                'id',
                'username',
                'capacityGb',
                'bytesUsed',
                'serviceResource.datacenter[name]',
                'serviceResourceBackendIpAddress',
                'activeTransactionCount',
                'fileNetworkMountAddress'
            ]
            kwargs['mask'] = ','.join(items)

        _filter = utils.NestedDict(kwargs.get('filter') or {})

        _filter['nasNetworkStorage']['serviceResource']['type']['type'] = \
            (utils.query_filter('!~ NAS'))

        _filter['nasNetworkStorage']['storageType']['keyName'] = (
            utils.query_filter('*FILE_STORAGE*'))
        if storage_type:
            _filter['nasNetworkStorage']['storageType']['keyName'] = (
                utils.query_filter('%s_FILE_STORAGE' % storage_type.upper()))

        if datacenter:
            _filter['nasNetworkStorage']['serviceResource']['datacenter'][
                'name'] = (utils.query_filter(datacenter))

        if username:
            _filter['nasNetworkStorage']['username'] = \
                (utils.query_filter(username))

        kwargs['filter'] = _filter.to_dict()
        return self.client.call('Account', 'getNasNetworkStorage', **kwargs)

    def get_file_volume_details(self, volume_id, **kwargs):
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
                'bytesUsed',
                'snapshotCapacityGb',
                'parentVolume.snapshotSizeBytes',
                'storageType.keyName',
                'serviceResource.datacenter[name]',
                'serviceResourceBackendIpAddress',
                'fileNetworkMountAddress',
                'storageTierLevel',
                'iops',
                'lunId',
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

    def get_file_volume_access_list(self, volume_id, **kwargs):
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

    def get_file_volume_snapshot_list(self, volume_id, **kwargs):
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
                                 subnet_ids=None,
                                 **kwargs):
        """Authorizes hosts to File Storage Volumes

        :param volume_id: The File volume to authorize hosts to
        :param hardware_ids: A List of SoftLayer_Hardware ids
        :param virtual_guest_ids: A List of SoftLayer_Virtual_Guest ids
        :param ip_address_ids: A List of SoftLayer_Network_Subnet_IpAddress ids
        :param subnet_ids: A List of SoftLayer_Network_Subnet ids
        :return: Returns an array of
                SoftLayer_Network_Storage_Allowed_Host objects
                which now have access to the given File volume
        """
        host_templates = []
        storage_utils.populate_host_templates(host_templates,
                                              hardware_ids,
                                              virtual_guest_ids,
                                              ip_address_ids,
                                              subnet_ids)

        return self.client.call('Network_Storage', 'allowAccessFromHostList',
                                host_templates, id=volume_id, **kwargs)

    def deauthorize_host_to_volume(self, volume_id,
                                   hardware_ids=None,
                                   virtual_guest_ids=None,
                                   ip_address_ids=None,
                                   subnet_ids=None,
                                   **kwargs):
        """Revokes authorization of hosts to File Storage Volumes

        :param volume_id: The File volume to deauthorize hosts to
        :param hardware_ids: A List of SoftLayer_Hardware ids
        :param virtual_guest_ids: A List of SoftLayer_Virtual_Guest ids
        :param ip_address_ids: A List of SoftLayer_Network_Subnet_IpAddress ids
        :param subnet_ids: A List of SoftLayer_Network_Subnet ids
        :return: Returns an array of
                SoftLayer_Network_Storage_Allowed_Host objects
                which have access to the given File volume
        """
        host_templates = []
        storage_utils.populate_host_templates(host_templates,
                                              hardware_ids,
                                              virtual_guest_ids,
                                              ip_address_ids,
                                              subnet_ids)

        return self.client.call('Network_Storage', 'removeAccessFromHostList',
                                host_templates, id=volume_id, **kwargs)

    def order_replicant_volume(self, volume_id, snapshot_schedule,
                               location, tier=None):
        """Places an order for a replicant file volume.

        :param volume_id: The ID of the primary volume to be replicated
        :param snapshot_schedule: The primary volume's snapshot
                                  schedule to use for replication
        :param location: The location for the ordered replicant volume
        :param tier: The tier (IOPS per GB) of the primary volume
        :return: Returns a SoftLayer_Container_Product_Order_Receipt
        """

        file_mask = 'billingItem[activeChildren],storageTierLevel,'\
                    'osType,snapshotCapacityGb,schedules,'\
                    'hourlySchedule,dailySchedule,weeklySchedule'
        file_volume = self.get_file_volume_details(volume_id,
                                                   mask=file_mask)

        order = storage_utils.prepare_replicant_order_object(
            self, volume_id, snapshot_schedule, location, tier,
            file_volume, 'file'
        )

        return self.client.call('Product_Order', 'placeOrder', order)

    def delete_snapshot(self, snapshot_id):
        """Deletes the specified snapshot object.

        :param snapshot_id: The ID of the snapshot object to delete.
        """
        return self.client.call('Network_Storage', 'deleteObject',
                                id=snapshot_id)

    def order_file_volume(self, storage_type, location, size, os_type=None,
                          iops=None, tier_level=None, snapshot_size=None):
        """Places an order for a file volume.

        :param storage_type: "performance_storage_iscsi" (performance)
                             or "storage_service_enterprise" (endurance)
        :param location: Datacenter in which to order iSCSI volume
        :param size: Size of the desired volume, in GB
        :param os_type: Not used for file storage orders, leave None
        :param iops: Number of IOPs for a "Performance" order
        :param tier_level: Tier level to use for an "Endurance" order
        :param snapshot_size: The size of optional snapshot space,
        if snapshot space should also be ordered (None if not ordered)
        """
        if os_type:
            raise exceptions.SoftLayerError(
                'OS type is not used on file storage orders')

        try:
            location_id = storage_utils.get_location_id(self, location)
        except ValueError:
            raise exceptions.SoftLayerError(
                "Invalid datacenter name specified. "
                "Please provide the lower case short name (e.g.: dal09)")

        base_type_name = 'SoftLayer_Container_Product_Order_Network_'
        package = storage_utils.get_package(self, storage_type)
        if storage_type == 'performance_storage_nfs':
            complex_type = base_type_name + 'PerformanceStorage_Nfs'
            prices = [
                storage_utils.find_performance_price(
                    package,
                    'performance_storage_nfs'
                    ),
                storage_utils.find_performance_space_price(package, size),
                storage_utils.find_performance_iops_price(package, size, iops),
            ]
        elif storage_type == 'storage_service_enterprise':
            complex_type = base_type_name + 'Storage_Enterprise'
            prices = [
                storage_utils.find_endurance_price(package, 'storage_file'),
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
                "File volume storage_type must be either "
                "Performance or Endurance")

        order = {
            'complexType': complex_type,
            'packageId': package['id'],
            'prices': prices,
            'quantity': 1,
            'location': location_id,
        }

        return self.client.call('Product_Order', 'placeOrder', order)

    def create_snapshot(self, volume_id, notes='', **kwargs):
        """Creates a snapshot on the given file volume.

        :param integer volume_id: The id of the volume
        :param string notes: The notes or "name" to assign the snapshot
        :return: Returns the id of the new snapshot
        """

        return self.client.call('Network_Storage', 'createSnapshot',
                                notes, id=volume_id, **kwargs)

    def enable_snapshots(self, volume_id, schedule_type, retention_count,
                         minute, hour, day_of_week, **kwargs):
        """Enables snapshots for a specific file volume at a given schedule

        :param integer volume_id: The id of the volume
        :param string schedule_type: 'HOURLY'|'DAILY'|'WEEKLY'
        :param integer retention_count: The number of snapshots to attempt to
        retain in this schedule
        :param integer minute: The minute of the hour at which HOURLY, DAILY,
        and WEEKLY snapshots should be taken
        :param integer hour: The hour of the day at which DAILY and WEEKLY
        snapshots should be taken
        :param string|integer day_of_week: The day of the week on which WEEKLY
        snapshots should be taken, either as a string ('SUNDAY') or integer
        ('0' is Sunday)
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
        """Disables snapshots for a specific file volume at a given schedule

        :param integer volume_id: The id of the volume
        :param string schedule_type: 'HOURLY'|'DAILY'|'WEEKLY'
        :return: Returns whether successfully disabled or not
        """

        return self.client.call('Network_Storage', 'disableSnapshots',
                                schedule_type, id=volume_id)

    def order_snapshot_space(self, volume_id, capacity, tier,
                             upgrade, **kwargs):
        """Orders snapshot space for the given file volume.

        :param integer volume_id: The ID of the volume
        :param integer capacity: The capacity to order, in GB
        :param float tier: The tier level of the file volume, in IOPS per GB
        :param boolean upgrade: Flag to indicate if this order is an upgrade
        :return: Returns a SoftLayer_Container_Product_Order_Receipt
        """

        package = storage_utils.get_package(self, 'storage_service_enterprise')
        file_mask = 'serviceResource.datacenter[id],'\
            'storageTierLevel,billingItem'
        file_volume = self.get_file_volume_details(volume_id,
                                                   mask=file_mask,
                                                   **kwargs)

        storage_type = file_volume['billingItem']['categoryCode']
        if storage_type != 'storage_service_enterprise':
            raise exceptions.SoftLayerError(
                "File volume storage_type must be Endurance")

        if tier is None:
            tier = storage_utils.find_endurance_tier_iops_per_gb(file_volume)
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
            'location': file_volume['serviceResource']['datacenter']['id'],
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
        :param boolean immediate: Cancel immediately or
        on anniversary date
        """

        file_volume = self.get_file_volume_details(
            volume_id,
            mask='mask[id,billingItem[activeChildren]]')
        children_array = file_volume['billingItem']['activeChildren']
        billing_item_id = None

        if 'activeChildren' not in file_volume['billingItem']:
            raise exceptions.SoftLayerError(
                'No snapshot space found to cancel')

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

    def restore_from_snapshot(self, volume_id, snapshot_id):
        """Restores a specific volume from a snapshot

        :param integer volume_id: The ID of the volume
        :param integer snapshot_id: The id of the restore point
        :return: Returns whether successfully restored or not
        """

        return self.client.call('Network_Storage', 'restoreFromSnapshot',
                                snapshot_id, id=volume_id)

    def cancel_file_volume(self, volume_id,
                           reason='No longer needed',
                           immediate=False):
        """Cancels the given file storage volume.

        :param integer volume_id: The volume ID
        :param string reason: The reason for cancellation
        :param boolean immediate: Cancel immediately or
        on anniversary date
        """
        file_volume = self.get_file_volume_details(
            volume_id,
            mask='mask[id,billingItem[id]]')
        billing_item_id = file_volume['billingItem']['id']

        return self.client['Billing_Item'].cancelItem(
            immediate,
            True,
            reason,
            id=billing_item_id)

    def failover_to_replicant(self, volume_id, replicant_id, immediate=False):
        """Failover to a volume replicant.

        :param integer volume_id: The ID of the volume
        :param integer replicant_id: ID of replicant to failover to
        :param boolean immediate: Flag indicating if failover is immediate
        :return: Returns whether failover was successful or not
        """

        return self.client.call('Network_Storage', 'failoverToReplicant',
                                replicant_id, immediate, id=volume_id)

    def failback_from_replicant(self, volume_id, replicant_id):
        """Failback from a volume replicant.

        :param integer volume_id: The ID of the volume
        :param integer replicant_id: ID of replicant to failback from
        :return: Returns whether failback was successful or not
        """

        return self.client.call('Network_Storage', 'failbackFromReplicant',
                                replicant_id, id=volume_id)
