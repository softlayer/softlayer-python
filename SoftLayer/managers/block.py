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
        """
        Returns a list of block volumes.
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

        call = 'getNetworkStorage'

        _filter = utils.NestedDict(kwargs.get('filter') or {})

        _filter['networkStorage']['serviceResource']['type']['type'] = (utils.query_filter('!~ ISCSI'))

        _filter['networkStorage']['storageType']['keyName'] = (
            utils.query_filter('*BLOCK_STORAGE'))
        if storage_type:
            _filter['networkStorage']['storageType']['keyName'] = (
                utils.query_filter('%s_BLOCK_STORAGE' % storage_type.upper()))

        if datacenter:
            _filter['networkStorage']['serviceResource']['datacenter'][
                'name'] = (
                utils.query_filter(datacenter))

        if username:
            _filter['networkStorage']['username'] = (
                utils.query_filter(username))

        kwargs['filter'] = _filter.to_dict()
        func = getattr(self.account, call)
        return func(**kwargs)

    def get_block_volume_details(self, volume_id, **kwargs):
        """
        Returns details about the specified volume.
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
        """
        Returns a list of authorized hosts for a specified volume.
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
        """
        Returns a list of snapshots for the specified volume.
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

    def order_block_volume(self, storage_type, location, size, os_type,
                           iops=None, tier_level=None, **kwargs):

        package = self._get_package(storage_type)
        if package['name'] == 'Performance':
            complexType = 'SoftLayer_Container_Product_Order_Network_PerformanceStorage_Iscsi'
            prices = self._get_item_prices_performance(package, size, iops)
        if package['name'] == 'Endurance':
            complexType = 'SoftLayer_Container_Product_Order_Network_Storage_Enterprise'
            prices = self._get_item_prices_endurance(package, size, tier_level)

        location_id = self._get_location_id(location)

        order = {
            'complexType': complexType,
            'packageId': package['id'],
            'osFormatType': {'keyName': os_type},
            'prices': prices,
            'quantity': 1,
            'location': location_id,
        }

        return self.product_order.placeOrder(order)

    def _get_package(self, category_code, **kwargs):
        """
        Returns a product packaged based on type of storage.
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
    def _get_item_prices_performance(package, size, iops, **kwargs):
        """
        Returns a collection of prices for a performance storage order.
        :param package: Package object
        :param size: Size of volume in GB
        :param iops: IOPs of volume
        :param kwargs:
        :return: Returns a collection of prices for a performance storage order.
        """
        prices = []
        for item in package['items']:
            for price in item['prices']:
                for category in price['categories']:
                    if price['locationGroupId'] == '' \
                            and (category[
                                     'categoryCode'] == 'performance_storage_iscsi'
                                 or (item['capacity'] == size
                                     and category[
                                        'categoryCode'] == 'performance_storage_space'
                                     )
                                 or (item['capacity'] == iops
                                     and category[
                                        'categoryCode'] == 'performance_storage_iops'
                                     and (price[
                                              'capacityRestrictionMinimum'] <= size <=
                                              price[
                                                  'capacityRestrictionMaximum'])
                                     )):
                        prices.append(price)
        return prices

    @staticmethod
    def _get_item_prices_endurance(package, size, tier_level, **kwargs):
        """
        Returns a collection of prices for a endurance storage order.
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

        prices = []
        for item in package['items']:
            for price in item['prices']:
                for category in price['categories']:
                    if price['locationGroupId'] == '' \
                            and (category[
                                     'categoryCode'] == 'storage_service_enterprise'
                                 or category['categoryCode'] == 'storage_block'
                                 or (category[
                                         'categoryCode'] == 'performance_storage_space'
                                     and price[
                                        'capacityRestrictionMinimum'] == tiers.get(
                                        tier_level) and item[
                                    'capacity'] == size
                                     )
                                 or (category[
                                         'categoryCode'] == 'storage_tier_level'
                                     and item['attributes'][0][
                                        'value'] == tiers.get(tier_level)
                                     )
                                 ):
                        prices.append(price)
        return prices

    def _get_location_id(self, location):
        """
        Returns location id
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
