"""
    SoftLayer.block
    ~~~~~~~~~~~~~~~
    Block Storage Manager

    :license: MIT, see LICENSE for more details.
"""
from SoftLayer.managers.storage import StorageManager
from SoftLayer.managers import storage_utils
from SoftLayer import utils

# pylint: disable=too-many-public-methods


class BlockStorageManager(StorageManager):
    """Manages SoftLayer Block Storage volumes.

    See product information here: https://www.ibm.com/cloud/block-storage
    """

    def list_block_volume_limit(self):
        """Returns a list of block volume count limit.

        :return: Returns a list of block volume count limit.
        """
        return self.get_volume_count_limits()

    def list_block_volumes(self, datacenter=None, username=None, storage_type=None, order=None, **kwargs):
        """Returns a list of block volumes.

        :param datacenter: Datacenter short name (e.g.: dal09)
        :param username: Name of volume.
        :param storage_type: Type of volume: Endurance or Performance
        :param order: Volume order id.
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
                'activeTransactionCount',
                'replicationPartnerCount'
            ]
            kwargs['mask'] = ','.join(items)

        _filter = utils.NestedDict(kwargs.get('filter') or {})

        _filter['iscsiNetworkStorage']['serviceResource']['type']['type'] = \
            (utils.query_filter('!~ ISCSI'))

        _filter['iscsiNetworkStorage']['storageType']['keyName'] = (
            utils.query_filter('*BLOCK_STORAGE*'))
        if storage_type:
            _filter['iscsiNetworkStorage']['storageType']['keyName'] = (
                utils.query_filter('%s_BLOCK_STORAGE*' % storage_type.upper()))

        if datacenter:
            _filter['iscsiNetworkStorage']['serviceResource']['datacenter'][
                'name'] = (utils.query_filter(datacenter))

        if username:
            _filter['iscsiNetworkStorage']['username'] = \
                (utils.query_filter(username))

        if order:
            _filter['iscsiNetworkStorage']['billingItem']['orderItem'][
                'order']['id'] = (utils.query_filter(order))

        kwargs['filter'] = _filter.to_dict()
        return self.client.call('Account', 'getIscsiNetworkStorage', iter=True, **kwargs)

    def get_block_volume_details(self, volume_id, **kwargs):
        """Returns details about the specified volume.

        :param volume_id: ID of volume.
        :param kwargs:
        :return: Returns details about the specified volume.
        """
        return self.get_volume_details(volume_id, **kwargs)

    def get_block_volume_access_list(self, volume_id, **kwargs):
        """Returns a list of authorized hosts for a specified volume.

        :param volume_id: ID of volume.
        :param kwargs:
        :return: Returns a list of authorized hosts for a specified volume.
        """
        return self.get_volume_access_list(volume_id, **kwargs)

    def get_block_volume_snapshot_list(self, volume_id, **kwargs):
        """Returns a list of snapshots for the specified volume.

        :param volume_id: ID of volume.
        :param kwargs:
        :return: Returns a list of snapshots for the specified volume.
        """
        return self.get_volume_snapshot_list(volume_id, **kwargs)

    def assign_subnets_to_acl(self, access_id, subnet_ids):
        """Assigns subnet records to ACL for the access host.

        access_id is the host_id obtained by: slcli block access-list <volume_id>

        :param integer access_id: id of the access host
        :param list subnet_ids: The ids of the subnets to be assigned
        :return: Returns int array of assigned subnet ids
        """
        return self.client.call('Network_Storage_Allowed_Host', 'assignSubnetsToAcl', subnet_ids, id=access_id)

    def remove_subnets_from_acl(self, access_id, subnet_ids):
        """Removes subnet records from ACL for the access host.

        access_id is the host_id obtained by: slcli block access-list <volume_id>

        :param integer access_id: id of the access host
        :param list subnet_ids: The ids of the subnets to be removed
        :return: Returns int array of removed subnet ids
        """
        return self.client.call('Network_Storage_Allowed_Host', 'removeSubnetsFromAcl', subnet_ids, id=access_id)

    def get_subnets_in_acl(self, access_id):
        """Returns a list of subnet records for the access host.

         access_id is the host_id obtained by: slcli block access-list <volume_id>

        :param integer access_id: id of the access host
        :return: Returns an array of SoftLayer_Network_Subnet objects
        """
        return self.client.call('Network_Storage_Allowed_Host', 'getSubnetsInAcl', id=access_id)

    def order_block_volume(self, storage_type, location, size, os_type,
                           iops=None, tier_level=None, snapshot_size=None,
                           service_offering='storage_as_a_service',
                           hourly_billing_flag=False):
        """Places an order for a block volume.

        :param storage_type: 'performance' or 'endurance'
        :param location: Datacenter in which to order iSCSI volume
        :param size: Size of the desired volume, in GB
        :param os_type: OS Type to use for volume alignment, see help for list
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
            snapshot_size, service_offering, 'block', hourly_billing_flag
        )

        order['osFormatType'] = {'keyName': os_type}

        return self.client.call('Product_Order', 'placeOrder', order)

    def cancel_block_volume(self, volume_id, reason='No longer needed', immediate=False):
        """Cancels the given block storage volume.

        :param integer volume_id: The volume ID
        :param string reason: The reason for cancellation
        :param boolean immediate_flag: Cancel immediately or on anniversary date
        """
        return self.cancel_volume(volume_id, reason, immediate)

    def set_credential_password(self, access_id, password):
        """Sets the password for an access host

        :param integer access_id: id of the access host
        :param string password: password to  set
        """

        return self.client.call('Network_Storage_Allowed_Host', 'setCredentialPassword',
                                password, id=access_id)

    def create_or_update_lun_id(self, volume_id, lun_id):
        """Set the LUN ID on a volume.

        :param integer volume_id: The id of the volume
        :param integer lun_id: LUN ID to set on the volume
        :return: a SoftLayer_Network_Storage_Property object
        """
        return self.client.call('Network_Storage', 'createOrUpdateLunId', lun_id, id=volume_id)

    def _get_ids_from_username(self, username):
        object_mask = "mask[id]"
        results = self.list_block_volumes(username=username, mask=object_mask)
        if results:
            return [result['id'] for result in results]
        return []
