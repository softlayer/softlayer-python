"""
    SoftLayer.block
    ~~~~~~~~~~~~~~~
    Block Storage Manager

    :license: MIT, see LICENSE for more details.
"""
from SoftLayer import exceptions
from SoftLayer import utils


ENDURANCE_TIERS = {
    0.25: 100,
    2: 200,
    4: 300,
}


class BlockStorageManager(utils.IdentifierMixin, object):
    """Manages Block Storage volumes."""

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
                'capacityGb',
                'bytesUsed',
                'serviceResource.datacenter[name]',
                'serviceResourceBackendIpAddress'
            ]
            kwargs['mask'] = ','.join(items)

        _filter = utils.NestedDict(kwargs.get('filter') or {})

        _filter['iscsiNetworkStorage']['serviceResource']['type']['type'] = \
            (utils.query_filter('!~ ISCSI'))

        _filter['iscsiNetworkStorage']['storageType']['keyName'] = (
            utils.query_filter('*BLOCK_STORAGE'))
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
            items = '''snapshots[
    id,
    notes,
    snapshotSizeBytes,
    storageType[keyName],
    snapshotCreationTimestamp
    hourlySchedule,
    dailySchedule,
    weeklySchedule
]'''
            kwargs['mask'] = ','.join(items)

        return self.client.call('Network_Storage', 'getSnapshots',
                                id=volume_id, **kwargs)

    def delete_snapshot(self, snapshot_id):
        """Deletes the specified snapshot object.

        :param snapshot_id: The ID of the snapshot object to delete.
        """
        return self.client.call('Network_Storage', 'deleteObject',
                                id=snapshot_id)

    def order_block_volume(self, storage_type, location, size, os_type,
                           iops=None, tier_level=None):
        """Places an order for a block volume.

        :param storage_type: "performance_storage_iscsi" (performance)
                             or "storage_service_enterprise" (endurance)
        :param location: Datacenter in which to order iSCSI volume
        :param size: Size of the desired volume, in GB
        :param os_type: OS Type to use for volume alignment, see help for list
        :param iops: Number of IOPs for a "Performance" order
        :param tier_level: Tier level to use for an "Endurance" order
        """

        try:
            location_id = self._get_location_id(location)
        except ValueError:
            raise exceptions.SoftLayerError(
                "Invalid datacenter name specified. "
                "Please provide the lower case short name (e.g.: dal09)")

        base_type_name = 'SoftLayer_Container_Product_Order_Network_'
        package = self._get_package(storage_type)
        if storage_type == 'performance_storage_iscsi':
            complex_type = base_type_name + 'PerformanceStorage_Iscsi'
            prices = [
                _find_performance_block_price(package),
                _find_performance_space_price(package, iops),
                _find_performance_iops_price(package, size, iops),
            ]
        elif storage_type == 'storage_service_enterprise':
            complex_type = base_type_name + 'Storage_Enterprise'
            prices = [
                _find_endurance_block_price(package),
                _find_endurance_price(package),
                _find_endurance_space_price(package, size, tier_level),
                _find_endurance_tier_price(package, tier_level),
            ]
        else:
            raise exceptions.SoftLayerError(
                "storage_type must be either Performance or Endurance")

        order = {
            'complexType': complex_type,
            'packageId': package['id'],
            'osFormatType': {'keyName': os_type},
            'prices': prices,
            'quantity': 1,
            'location': location_id,
        }

        return self.client.call('Product_Order', 'placeOrder', order)

    def _get_package(self, category_code):
        """Returns a product packaged based on type of storage.

        :param category_code: Category code of product package.
        :return: Returns a packaged based on type of storage.
        """

        _filter = utils.NestedDict({})
        _filter['categories']['categoryCode'] = (
            utils.query_filter(category_code))
        _filter['statusCode'] = (utils.query_filter('ACTIVE'))

        packages = self.client.call('Product_Package', 'getAllObjects',
                                    filter=_filter.to_dict(),
                                    mask="""
id,
name,
items[prices[categories],attributes]
""")
        if len(packages) == 0:
            raise ValueError('No packages were found for %s' % category_code)
        if len(packages) > 1:
            raise ValueError('More than one package was found for %s'
                             % category_code)

        return packages[0]

    def _get_location_id(self, location):
        """Returns location id

        :param location: Datacenter short name
        :return: Returns location id
        """
        loc_svc = self.client['Location_Datacenter']
        datacenters = loc_svc.getDatacenters(mask='mask[longName,id,name]')
        for datacenter in datacenters:
            if datacenter['name'] == location:
                location = datacenter['id']
                return location
        raise ValueError('Invalid datacenter name specified.')

    def cancel_block_volume(self, volume_id,
                            reason='No longer needed',
                            immediate=False):
        """Cancels the given block storage volume.

        :param integer volume_id: the volume ID
        :param string reason: The reason for cancellation
        :param boolean immediate_flag: Cancel immediately or
        on anniversary date
        """
        block_volume = self.get_block_volume_details(
            volume_id,
            mask='mask[id,billingItem[id]]')
        billing_item_id = block_volume['billingItem']['id']

        self.client['Billing_Item'].cancelItem(
            immediate,
            True,
            reason,
            id=billing_item_id)


def _find_endurance_block_price(package):
    for item in package['items']:
        for price in item['prices']:
            if price['locationGroupId'] != '':
                continue

            if not _has_category(price['categories'], 'storage_block'):
                continue

            return price

    raise ValueError("Could not find price for block storage")


def _find_endurance_price(package):
    for item in package['items']:
        for price in item['prices']:
            if price['locationGroupId'] != '':
                continue

            if not _has_category(price['categories'],
                                 'storage_service_enterprise'):
                continue

            return price

    raise ValueError("Could not find price for endurance block storage")


def _find_endurance_space_price(package, size, tier_level):
    for item in package['items']:
        if int(item['capacity']) != size:
            continue

        for price in item['prices']:
            # Only collect prices from valid location groups.
            if price['locationGroupId'] != '':
                continue

            if not _has_category(price['categories'],
                                 'performance_storage_space'):
                continue

            level = ENDURANCE_TIERS.get(tier_level)
            if level < int(price['capacityRestrictionMinimum']):
                continue

            if level > int(price['capacityRestrictionMaximum']):
                continue

            return price

    raise ValueError("Could not find price for disk space")


def _find_endurance_tier_price(package, tier_level):
    for item in package['items']:
        for attribute in item.get('attributes', []):
            if int(attribute['value']) == ENDURANCE_TIERS.get(tier_level):
                break
        else:
            continue

        for price in item['prices']:
            # Only collect prices from valid location groups.
            if price['locationGroupId'] != '':
                continue

            if not _has_category(price['categories'], 'storage_tier_level'):
                continue

            return price

    raise ValueError("Could not find price for tier")


def _find_performance_block_price(package):
    for item in package['items']:
        for price in item['prices']:
            # Only collect prices from valid location groups.
            if price['locationGroupId'] != '':
                continue

            if not _has_category(price['categories'],
                                 'performance_storage_iscsi'):
                continue

            return price

    raise ValueError("Could not find price for performance storage")


def _find_performance_space_price(package, size):
    for item in package['items']:
        if int(item['capacity']) != size:
            continue

        for price in item['prices']:
            # Only collect prices from valid location groups.
            if price['locationGroupId'] != '':
                continue

            if not _has_category(price['categories'],
                                 'performance_storage_space'):
                continue

            return price

    raise ValueError("Could not find price for disk space")


def _find_performance_iops_price(package, size, iops):
    for item in package['items']:
        if int(item['capacity']) != int(iops):
            continue

        for price in item['prices']:
            # Only collect prices from valid location groups.
            if price['locationGroupId'] != '':
                continue

            if not _has_category(price['categories'],
                                 'performance_storage_iops'):
                continue

            if size < int(price['capacityRestrictionMinimum']):
                continue

            if size > int(price['capacityRestrictionMaximum']):
                continue

            return price

    raise ValueError("Could not find price for iops")


def _has_category(categories, category_code):
    return any(
        True
        for category
        in categories
        if category['categoryCode'] == category_code
    )
