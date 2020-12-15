"""
    SoftLayer.file
    ~~~~~~~~~~~~~~~
    File Storage Manager

    :license: MIT, see LICENSE for more details.
"""
from SoftLayer.managers.storage import StorageManager
from SoftLayer.managers import storage_utils
from SoftLayer import utils

# pylint: disable=too-many-public-methods


class FileStorageManager(StorageManager):
    """Manages file Storage volumes."""

    def list_file_volume_limit(self):
        """Returns a list of block volume count limit.

        :return: Returns a list of block volume count limit.
        """
        return self.get_volume_count_limits()

    def list_file_volumes(self, datacenter=None, username=None, storage_type=None, order=None, **kwargs):
        """Returns a list of file volumes.

        :param datacenter: Datacenter short name (e.g.: dal09)
        :param username: Name of volume.
        :param storage_type: Type of volume: Endurance or Performance
        :param order: Volume order id.
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
                'fileNetworkMountAddress',
                'replicationPartnerCount'
            ]
            kwargs['mask'] = ','.join(items)

        _filter = utils.NestedDict(kwargs.get('filter') or {})

        _filter['nasNetworkStorage']['serviceResource']['type']['type'] = \
            (utils.query_filter('!~ NAS'))

        _filter['nasNetworkStorage']['storageType']['keyName'] = (
            utils.query_filter('*FILE_STORAGE*'))
        if storage_type:
            _filter['nasNetworkStorage']['storageType']['keyName'] = (
                utils.query_filter('%s_FILE_STORAGE*' % storage_type.upper()))

        if datacenter:
            _filter['nasNetworkStorage']['serviceResource']['datacenter'][
                'name'] = (utils.query_filter(datacenter))

        if username:
            _filter['nasNetworkStorage']['username'] = \
                (utils.query_filter(username))

        if order:
            _filter['nasNetworkStorage']['billingItem']['orderItem'][
                'order']['id'] = (utils.query_filter(order))

        kwargs['filter'] = _filter.to_dict()
        return self.client.call('Account', 'getNasNetworkStorage', iter=True, **kwargs)

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
                'provisionedIops',
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
                'notes',
            ]
            kwargs['mask'] = ','.join(items)
        return self.get_volume_details(volume_id, **kwargs)

    def get_file_volume_access_list(self, volume_id, **kwargs):
        """Returns a list of authorized hosts for a specified volume.

        :param volume_id: ID of volume.
        :param kwargs:
        :return: Returns a list of authorized hosts for a specified volume.
        """
        return self.get_volume_access_list(volume_id, **kwargs)

    def get_file_volume_snapshot_list(self, volume_id, **kwargs):
        """Returns a list of snapshots for the specified volume.

        :param volume_id: ID of volume.
        :param kwargs:
        :return: Returns a list of snapshots for the specified volume.
        """
        return self.get_volume_snapshot_list(volume_id, **kwargs)

    def order_file_volume(self, storage_type, location, size,
                          iops=None, tier_level=None, snapshot_size=None,
                          service_offering='storage_as_a_service',
                          hourly_billing_flag=False):
        """Places an order for a file volume.

        :param storage_type: 'performance' or 'endurance'
        :param location: Name of the datacenter in which to order the volume
        :param size: Size of the desired volume, in GB
        :param iops: Number of IOPs for a "Performance" order
        :param tier_level: Tier level to use for an "Endurance" order
        :param snapshot_size: The size of optional snapshot space,
            if snapshot space should also be ordered (None if not ordered)
        :param service_offering: Requested offering package to use in the order
            ('storage_as_a_service', 'enterprise', or 'performance')
        :param hourly_billing_flag: Billing type, monthly (False)
            or hourly (True), default to monthly.
        """
        order = storage_utils.prepare_volume_order_object(
            self, storage_type, location, size, iops, tier_level,
            snapshot_size, service_offering, 'file', hourly_billing_flag
        )

        return self.client.call('Product_Order', 'placeOrder', order)

    def cancel_file_volume(self, volume_id, reason='No longer needed', immediate=False):
        """Cancels the given file storage volume.

        :param integer volume_id: The volume ID
        :param string reason: The reason for cancellation
        :param boolean immediate: Cancel immediately or on anniversary date
        """
        return self.cancel_volume(volume_id, reason, immediate)

    def _get_ids_from_username(self, username):
        object_mask = "mask[id]"
        results = self.list_file_volumes(username=username, mask=object_mask)
        if results:
            return [result['id'] for result in results]
        return []
