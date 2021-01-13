"""
    SoftLayer.storage
    ~~~~~~~~~~~~~~~
    Network Storage Manager

    :license: MIT, see LICENSE for more details.
"""
from SoftLayer import exceptions
from SoftLayer.managers import storage_utils
from SoftLayer import utils


# pylint: disable=too-many-public-methods


class StorageManager(utils.IdentifierMixin, object):
    """"Base class for File and Block storage managers

    Any shared code between File and Block should ideally go here.

    :param SoftLayer.API.BaseClient client: the client instance
    """

    def __init__(self, client):
        self.configuration = {}
        self.client = client
        self.resolvers = [self._get_ids_from_username]

    def get_volume_count_limits(self):
        """Returns a list of block volume count limit.

        :return: Returns a list of block volume count limit.
        """
        return self.client.call('Network_Storage', 'getVolumeCountLimits')

    def get_volume_details(self, volume_id, **kwargs):
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
        return self.client.call('Network_Storage', 'getObject', id=volume_id, **kwargs)

    def get_volume_access_list(self, volume_id, **kwargs):
        """Returns a list of authorized hosts for a specified volume.

        :param volume_id: ID of volume.
        :param kwargs:
        :return: Returns a list of authorized hosts for a specified volume.
        """
        if 'mask' not in kwargs:
            items = [
                'id',
                'allowedVirtualGuests[allowedHost[credential, sourceSubnet]]',
                'allowedHardware[allowedHost[credential]]',
                'allowedSubnets[allowedHost[credential]]',
                'allowedIpAddresses[allowedHost[credential]]',
            ]
            kwargs['mask'] = ','.join(items)
        return self.client.call('Network_Storage', 'getObject', id=volume_id, **kwargs)

    def get_volume_snapshot_list(self, volume_id, **kwargs):
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
                'intervalSchedule',
                'hourlySchedule',
                'dailySchedule',
                'weeklySchedule'
            ]

            kwargs['mask'] = ','.join(items)

        return self.client.call('Network_Storage', 'getSnapshots', id=volume_id, **kwargs)

    def authorize_host_to_volume(self, volume_id, hardware_ids=None, virtual_guest_ids=None,
                                 ip_address_ids=None, subnet_ids=None):
        """Authorizes hosts to Storage Volumes

        :param volume_id: The File volume to authorize hosts to
        :param hardware_ids: A List of SoftLayer_Hardware ids
        :param virtual_guest_ids: A List of SoftLayer_Virtual_Guest ids
        :param ip_address_ids: A List of SoftLayer_Network_Subnet_IpAddress ids
        :param subnet_ids: A List of SoftLayer_Network_Subnet ids. Only use with File volumes.
        :return: Returns an array of SoftLayer_Network_Storage_Allowed_Host objects
                which now have access to the given volume
        """
        host_templates = storage_utils.populate_host_templates(hardware_ids, virtual_guest_ids,
                                                               ip_address_ids, subnet_ids)

        return self.client.call('Network_Storage', 'allowAccessFromHostList', host_templates, id=volume_id)

    def deauthorize_host_to_volume(self, volume_id, hardware_ids=None, virtual_guest_ids=None,
                                   ip_address_ids=None, subnet_ids=None):
        """Revokes authorization of hosts to File Storage Volumes

        :param volume_id: The File volume to deauthorize hosts to
        :param hardware_ids: A List of SoftLayer_Hardware ids
        :param virtual_guest_ids: A List of SoftLayer_Virtual_Guest ids
        :param ip_address_ids: A List of SoftLayer_Network_Subnet_IpAddress ids
        :param subnet_ids: A List of SoftLayer_Network_Subnet ids. Only use with File volumes
        :return: Returns an array of SoftLayer_Network_Storage_Allowed_Host objects
                which have access to the given File volume
        """
        host_templates = storage_utils.populate_host_templates(hardware_ids, virtual_guest_ids,
                                                               ip_address_ids, subnet_ids)

        return self.client.call('Network_Storage', 'removeAccessFromHostList', host_templates, id=volume_id)

    def get_replication_partners(self, volume_id):
        """Acquires list of replicant volumes pertaining to the given volume.

        :param volume_id: The ID of the primary volume to be replicated
        :return: Returns an array of SoftLayer_Location objects
        """
        return self.client.call('Network_Storage', 'getReplicationPartners', id=volume_id)

    def get_replication_locations(self, volume_id):
        """Acquires list of the datacenters to which a volume can be replicated.

        :param volume_id: The ID of the primary volume to be replicated
        :return: Returns an array of SoftLayer_Network_Storage objects
        """
        return self.client.call('Network_Storage', 'getValidReplicationTargetDatacenterLocations', id=volume_id)

    def order_replicant_volume(self, volume_id, snapshot_schedule, location, tier=None, os_type=None):
        """Places an order for a replicant volume.

        :param volume_id: The ID of the primary volume to be replicated
        :param snapshot_schedule: The primary volume's snapshot
                                  schedule to use for replication
        :param location: The location for the ordered replicant volume
        :param tier: The tier (IOPS per GB) of the primary volume
        :param os_type: The OS type of the primary volume
        :return: Returns a SoftLayer_Container_Product_Order_Receipt
        """

        block_mask = 'billingItem[activeChildren,hourlyFlag],' \
                     'storageTierLevel,osType,staasVersion,' \
                     'hasEncryptionAtRest,snapshotCapacityGb,schedules,' \
                     'intervalSchedule,hourlySchedule,dailySchedule,' \
                     'weeklySchedule,storageType[keyName],provisionedIops'
        block_volume = self.get_volume_details(volume_id, mask=block_mask)

        storage_class = storage_utils.block_or_file(block_volume['storageType']['keyName'])

        order = storage_utils.prepare_replicant_order_object(
            self, snapshot_schedule, location, tier, block_volume, storage_class
        )

        if storage_class == 'block':
            if os_type is None:
                if isinstance(utils.lookup(block_volume, 'osType', 'keyName'), str):
                    os_type = block_volume['osType']['keyName']
                else:
                    raise exceptions.SoftLayerError(
                        "Cannot find primary volume's os-type "
                        "automatically; must specify manually")
            order['osFormatType'] = {'keyName': os_type}

        return self.client.call('Product_Order', 'placeOrder', order)

    def order_duplicate_volume(self, origin_volume_id, origin_snapshot_id=None, duplicate_size=None,
                               duplicate_iops=None, duplicate_tier_level=None, duplicate_snapshot_size=None,
                               hourly_billing_flag=False, dependent_duplicate=False):
        """Places an order for a duplicate volume.

        :param origin_volume_id: The ID of the origin volume to be duplicated
        :param origin_snapshot_id: Origin snapshot ID to use for duplication
        :param duplicate_size: Size/capacity for the duplicate volume
        :param duplicate_iops: The IOPS per GB for the duplicate volume
        :param duplicate_tier_level: Tier level for the duplicate volume
        :param duplicate_snapshot_size: Snapshot space size for the duplicate
        :param hourly_billing_flag: Billing type, monthly (False) or hourly (True), default to monthly.
        :return: Returns a SoftLayer_Container_Product_Order_Receipt
        """

        block_mask = 'id,billingItem[location,hourlyFlag],snapshotCapacityGb,' \
                     'storageType[keyName],capacityGb,originalVolumeSize,' \
                     'provisionedIops,storageTierLevel,osType[keyName],' \
                     'staasVersion,hasEncryptionAtRest'
        origin_volume = self.get_volume_details(origin_volume_id, mask=block_mask)
        storage_class = storage_utils.block_or_file(origin_volume['storageType']['keyName'])

        order = storage_utils.prepare_duplicate_order_object(
            self, origin_volume, duplicate_iops, duplicate_tier_level,
            duplicate_size, duplicate_snapshot_size, storage_class, hourly_billing_flag
        )

        if storage_class == 'block':
            if isinstance(utils.lookup(origin_volume, 'osType', 'keyName'), str):
                os_type = origin_volume['osType']['keyName']
            else:
                raise exceptions.SoftLayerError("Cannot find origin volume's os-type")

            order['osFormatType'] = {'keyName': os_type}

        if origin_snapshot_id is not None:
            order['duplicateOriginSnapshotId'] = origin_snapshot_id
        if dependent_duplicate:
            # if isDependentDuplicateFlag is set to ANYTHING, it is considered dependent.
            order['isDependentDuplicateFlag'] = 1

        return self.client.call('Product_Order', 'placeOrder', order)

    def order_modified_volume(self, volume_id, new_size=None, new_iops=None, new_tier_level=None):
        """Places an order for modifying an existing block volume.

        :param volume_id: The ID of the volume to be modified
        :param new_size: The new size/capacity for the volume
        :param new_iops: The new IOPS for the volume
        :param new_tier_level: The new tier level for the volume
        :return: Returns a SoftLayer_Container_Product_Order_Receipt
        """

        mask_items = [
            'id',
            'billingItem',
            'storageType[keyName]',
            'capacityGb',
            'provisionedIops',
            'storageTierLevel',
            'staasVersion',
            'hasEncryptionAtRest',
        ]
        block_mask = ','.join(mask_items)
        volume = self.get_volume_details(volume_id, mask=block_mask)

        order = storage_utils.prepare_modify_order_object(
            self, volume, new_iops, new_tier_level, new_size
        )

        return self.client.call('Product_Order', 'placeOrder', order)

    def volume_set_note(self, volume_id, note):
        """Set the notes for an existing block volume.

        :param volume_id: The ID of the volume to be modified
        :param note: the note
        :return: Returns true if success
        """
        template = {'notes': note}
        return self.client.call('SoftLayer_Network_Storage', 'editObject', template, id=volume_id)

    def delete_snapshot(self, snapshot_id):
        """Deletes the specified snapshot object.

        :param snapshot_id: The ID of the snapshot object to delete.
        """
        return self.client.call('Network_Storage', 'deleteObject', id=snapshot_id)

    def create_snapshot(self, volume_id, notes='', **kwargs):
        """Creates a snapshot on the given block volume.

        :param integer volume_id: The id of the volume
        :param string notes: The notes or "name" to assign the snapshot
        :return: Returns the id of the new snapshot
        """
        return self.client.call('Network_Storage', 'createSnapshot', notes, id=volume_id, **kwargs)

    def order_snapshot_space(self, volume_id, capacity, tier, upgrade, **kwargs):
        """Orders snapshot space for the given block volume.

        :param integer volume_id: The id of the volume
        :param integer capacity: The capacity to order, in GB
        :param float tier: The tier level of the block volume, in IOPS per GB
        :param boolean upgrade: Flag to indicate if this order is an upgrade
        :return: Returns a SoftLayer_Container_Product_Order_Receipt
        """
        object_mask = 'id,billingItem[location,hourlyFlag],' \
                      'storageType[keyName],storageTierLevel,provisionedIops,' \
                      'staasVersion,hasEncryptionAtRest'
        volume = self.get_volume_details(volume_id, mask=object_mask, **kwargs)

        order = storage_utils.prepare_snapshot_order_object(self, volume, capacity, tier, upgrade)

        return self.client.call('Product_Order', 'placeOrder', order)

    def cancel_snapshot_space(self, volume_id, reason='No longer needed', immediate=False):
        """Cancels snapshot space for a given volume.

        :param integer volume_id: The volume ID
        :param string reason: The reason for cancellation
        :param boolean immediate_flag: Cancel immediately or on anniversary date
        """

        object_mask = 'mask[id,billingItem[activeChildren,hourlyFlag]]'
        volume = self.get_volume_details(volume_id, mask=object_mask)

        if 'activeChildren' not in volume['billingItem']:
            raise exceptions.SoftLayerError('No snapshot space found to cancel')

        children_array = volume['billingItem']['activeChildren']
        billing_item_id = None

        for child in children_array:
            if child['categoryCode'] == 'storage_snapshot_space':
                billing_item_id = child['id']
                break

        if not billing_item_id:
            raise exceptions.SoftLayerError('No snapshot space found to cancel')

        if utils.lookup(volume, 'billingItem', 'hourlyFlag'):
            immediate = True

        return self.client.call('SoftLayer_Billing_Item', 'cancelItem', immediate, True, reason, id=billing_item_id)

    def enable_snapshots(self, volume_id, schedule_type, retention_count, minute, hour, day_of_week, **kwargs):
        """Enables snapshots for a specific block volume at a given schedule

        :param integer volume_id: The id of the volume
        :param string schedule_type: 'HOURLY'|'DAILY'|'WEEKLY'
        :param integer retention_count: Number of snapshots to be kept
        :param integer minute: Minute when to take snapshot
        :param integer hour: Hour when to take snapshot
        :param string day_of_week: Day when to take snapshot
        :return: Returns whether successfully scheduled or not
        """
        return self.client.call('Network_Storage', 'enableSnapshots', schedule_type, retention_count,
                                minute, hour, day_of_week, id=volume_id, **kwargs)

    def disable_snapshots(self, volume_id, schedule_type):
        """Disables snapshots for a specific block volume at a given schedule

        :param integer volume_id: The id of the volume
        :param string schedule_type: 'HOURLY'|'DAILY'|'WEEKLY'
        :return: Returns whether successfully disabled or not
        """
        return self.client.call('Network_Storage', 'disableSnapshots', schedule_type, id=volume_id)

    def list_volume_schedules(self, volume_id):
        """Lists schedules for a given volume

        :param integer volume_id: The id of the volume
        :return: Returns list of schedules assigned to a given volume
        """
        object_mask = 'schedules[type,properties[type]]'
        volume_detail = self.client.call('Network_Storage', 'getObject', id=volume_id, mask=object_mask)

        return utils.lookup(volume_detail, 'schedules')

    def restore_from_snapshot(self, volume_id, snapshot_id):
        """Restores a specific volume from a snapshot

        :param integer volume_id: The id of the volume
        :param integer snapshot_id: The id of the restore point
        :return: Returns whether succesfully restored or not
        """
        return self.client.call('Network_Storage', 'restoreFromSnapshot', snapshot_id, id=volume_id)

    def failover_to_replicant(self, volume_id, replicant_id):
        """Failover to a volume replicant.

        :param integer volume_id: The id of the volume
        :param integer replicant_id: ID of replicant to failover to
        :return: Returns whether failover was successful or not
        """
        return self.client.call('Network_Storage', 'failoverToReplicant', replicant_id, id=volume_id)

    def disaster_recovery_failover_to_replicant(self, volume_id, replicant_id):
        """Disaster Recovery Failover to a volume replicant.

        :param integer volume_id: The id of the volume
        :param integer replicant: ID of replicant to failover to
        :return: Returns whether failover to successful or not
        """
        return self.client.call('Network_Storage', 'disasterRecoveryFailoverToReplicant', replicant_id, id=volume_id)

    def failback_from_replicant(self, volume_id):
        """Failback from a volume replicant.

        :param integer volume_id: The id of the volume
        :return: Returns whether failback was successful or not
        """
        return self.client.call('Network_Storage', 'failbackFromReplicant', id=volume_id)

    def cancel_volume(self, volume_id, reason='No longer needed', immediate=False):
        """Cancels the given storage volume.

        :param integer volume_id: The volume ID
        :param string reason: The reason for cancellation
        :param boolean immediate_flag: Cancel immediately or on anniversary date
        """
        object_mask = 'mask[id,billingItem[id,hourlyFlag]]'
        volume = self.get_volume_details(volume_id, mask=object_mask)

        if 'billingItem' not in volume:
            raise exceptions.SoftLayerError("Storage Volume was already cancelled")

        billing_item_id = volume['billingItem']['id']

        if utils.lookup(volume, 'billingItem', 'hourlyFlag'):
            immediate = True

        return self.client.call('SoftLayer_Billing_Item', 'cancelItem', immediate, True, reason, id=billing_item_id)

    def refresh_dupe(self, volume_id, snapshot_id):
        """"Refresh a duplicate volume with a snapshot from its parent.

        :param integer volume_id: The id of the volume
        :param integer snapshot_id: The id of the snapshot
        """
        return self.client.call('Network_Storage', 'refreshDuplicate', snapshot_id, id=volume_id)

    def convert_dep_dupe(self, volume_id):
        """Convert a dependent duplicate volume to an independent volume.

        :param integer volume_id: The id of the volume.
        """
        return self.client.call('Network_Storage', 'convertCloneDependentToIndependent', id=volume_id)
