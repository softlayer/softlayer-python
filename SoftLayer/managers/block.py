"""
    SoftLayer.block
    ~~~~~~~~~~~~~~~
    Block Storage Manager

    :license: MIT, see LICENSE for more details.
"""
from SoftLayer import exceptions
from SoftLayer import utils


class BlockStorageManager(utils.IdentifierMixin, object):
    """Manages Block Storage volumes."""

    def __init__(self, client):
        self.configuration = {}
        self.client = client
        self.account = client['Account']
        self.product_package = self.client['Product_Package']
        self.block_svc = self.client['Network_Storage']
        self.block_os_types = self.client['Network_Storage_Iscsi_OS_Type']
        self.product_order = self.client['Product_Order']

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
            kwargs['mask'] = "mask[%s]" % ','.join(items)

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
            kwargs['mask'] = "mask[%s]" % ','.join(items)
        return self.block_svc.getObject(id=volume_id, **kwargs)

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
            kwargs['mask'] = "mask[%s]" % ','.join(items)
        return self.block_svc.getObject(id=volume_id, **kwargs)

    def get_block_volume_snapshot_list(self, volume_id, **kwargs):
        """Returns a list of snapshots for the specified volume.

        :param volume_id: ID of volume.
        :param kwargs:
        :return: Returns a list of snapshots for the specified volume.
        """
        if 'mask' not in kwargs:
            items = [
                'snapshots.id',
                'snapshots.notes',
                'snapshots.snapshotSizeBytes',
                'snapshots.storageType.keyName',
                'snapshots.snapshotCreationTimestamp',
                'snapshots[hourlySchedule,dailySchedule,weeklySchedule]',
            ]
            kwargs['mask'] = "mask[%s]" % ','.join(items)
        return self.block_svc.getObject(id=volume_id, **kwargs)

    def delete_snapshot(self, snapshot_id):
        """Deletes the specified snapshot object.

        :param snapshot_id: The ID of the snapshot object to delete.
        """
        return self.block_svc.deleteObject(id=snapshot_id)

    def order_block_volume(self, storage_type, location, size, os_type,
                           iops=None, tier_level=None):
        """Places an order for a block volume.

        :param storage_type: "Performance" or "Endurance"
        :param location: Datacenter in which to order iSCSI volume
        :param size: Size of the desired volume, in GB
        :param os_type: OS Type to use for volume alignment, see help for list
        :param iops: Number of IOPs for a "Performance" order
        :param tier_level: Tier level to use for an "Endurance" order
        """

        try:
            location_id = self._get_location_id(location)
        except ValueError:
            raise exceptions.SoftLayerError("Invalid datacenter name specified")

        base_type_name = 'SoftLayer_Container_Product_Order_Network_'
        package = self._get_package(storage_type)
        if package['name'] == 'Performance':
            complex_type = base_type_name + 'PerformanceStorage_Iscsi'
            prices = self._get_item_prices_performance(package, size, iops)
        elif package['name'] == 'Endurance':
            complex_type = base_type_name + 'Storage_Enterprise'
            prices = self._get_item_prices_endurance(package, size, tier_level)
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

        return self.product_order.placeOrder(order)

    def _get_package(self, category_code, **kwargs):
        """Returns a product packaged based on type of storage.

        :param category_code: Category code of product package.
        :param kwargs:
        :return: Returns a packaged based on type of storage.
        """
        if 'mask' not in kwargs:
            items = [
                'id',
                'name',
                'items',
                'items[prices[categories],attributes]'
            ]
            kwargs['mask'] = "mask[%s]" % ','.join(items)

        _filter = utils.NestedDict(kwargs.get('filter') or {})
        _filter['categories']['categoryCode'] = (
            utils.query_filter(category_code))
        _filter['statusCode'] = (utils.query_filter('ACTIVE'))
        kwargs['filter'] = _filter.to_dict()

        func = getattr(self.product_package, 'getAllObjects')
        return func(**kwargs).pop()

    @staticmethod
    def _get_item_prices_performance(package, size, iops):
        """Returns a collection of prices for performance storage.

        :param package: Package object
        :param size: Size of volume in GB
        :param iops: IOPs of volume
        :param kwargs:
        :return: Returns a collection of prices for performance storage.
        """
        parent_category_code = 'performance_storage_iscsi'
        space_category_code = 'performance_storage_space'
        iops_category_code = 'performance_storage_iops'

        found_space_price = False
        found_iops_price = False

        prices = []
        for item in package['items']:
            for price in item['prices']:
                for category in price['categories']:
                    if price['locationGroupId'] == '':
                        # Find the parent-level price object.
                        if category['categoryCode'] == parent_category_code:
                            prices.append(price)
                        # Find the valid space price object.
                        elif (category['categoryCode'] == space_category_code
                              and item['capacity'] == size):
                            prices.append(price)
                            found_space_price = True
                        # Find the valid iops price object.
                        elif (category['categoryCode'] == iops_category_code
                              and item['capacity'] == iops
                              and (price['capacityRestrictionMinimum'] <= size
                                   <= price['capacityRestrictionMaximum'])):
                            prices.append(price)
                            found_iops_price = True

        if found_space_price is False or found_iops_price is False:
            raise ValueError(
                "No prices found for the requested size and iops.")

        return prices

    @staticmethod
    def _get_item_prices_endurance(package, size, tier_level):
        """Returns a collection of prices for a endurance storage order.

        :param package: Package object
        :param size: Size of volume in GB
        :param iops: IOPs of volume
        :param kwargs:
        :return: Returns a collection of prices for a endurance storage order.
        """

        tiers = {
            '0.25': '100',
            '2': '200',
            '4': '300'
        }

        endurance_parent_category_codes = [
            'storage_service_enterprise',
            'storage_block',
        ]

        space_category_code = 'performance_storage_space'
        tier_category_code = 'storage_tier_level'

        found_space_price = False
        found_iops_price = False

        prices = []
        for item in package['items']:
            for price in item['prices']:
                for category in price['categories']:
                    # Only collect prices from valid location groups.
                    if price['locationGroupId'] == '':
                        # Find the parent-level price object.
                        if any(category['categoryCode'] in s
                               for s in endurance_parent_category_codes):
                            prices.append(price)
                        # Find the valid space price object.
                        elif (category['categoryCode'] == space_category_code
                              and price['capacityRestrictionMinimum'] ==
                              tiers.get(tier_level)
                              and item['capacity'] == size):
                            prices.append(price)
                            found_space_price = True
                        # Find the valid tier price object.
                        elif (category['categoryCode'] == tier_category_code
                              and item['attributes'][0]['value'] ==
                              tiers.get(tier_level)):
                            prices.append(price)
                            found_iops_price = True

        if found_space_price is False or found_iops_price is False:
            raise ValueError(
                "No prices found for the requested size and tier.")

        return prices

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
