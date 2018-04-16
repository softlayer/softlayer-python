"""
    SoftLayer.storage_utils
    ~~~~~~~~~~~~~~~
    Utility functions used by File and Block Storage Managers

    :license: MIT, see LICENSE for more details.
"""
from SoftLayer import exceptions
from SoftLayer import utils

# pylint: disable=too-many-lines


ENDURANCE_TIERS = {
    0.25: 100,
    2: 200,
    4: 300,
    10: 1000,
}


def populate_host_templates(host_templates,
                            hardware_ids=None,
                            virtual_guest_ids=None,
                            ip_address_ids=None,
                            subnet_ids=None):
    """Populate the given host_templates array with the IDs provided

    :param host_templates: The array to which host templates will be added
    :param hardware_ids: A List of SoftLayer_Hardware ids
    :param virtual_guest_ids: A List of SoftLayer_Virtual_Guest ids
    :param ip_address_ids: A List of SoftLayer_Network_Subnet_IpAddress ids
    :param subnet_ids: A List of SoftLayer_Network_Subnet ids
    """
    if hardware_ids is not None:
        for hardware_id in hardware_ids:
            host_templates.append({
                'objectType': 'SoftLayer_Hardware',
                'id': hardware_id
            })

    if virtual_guest_ids is not None:
        for virtual_guest_id in virtual_guest_ids:
            host_templates.append({
                'objectType': 'SoftLayer_Virtual_Guest',
                'id': virtual_guest_id
            })

    if ip_address_ids is not None:
        for ip_address_id in ip_address_ids:
            host_templates.append({
                'objectType': 'SoftLayer_Network_Subnet_IpAddress',
                'id': ip_address_id
            })

    if subnet_ids is not None:
        for subnet_id in subnet_ids:
            host_templates.append({
                'objectType': 'SoftLayer_Network_Subnet',
                'id': subnet_id
            })


def get_package(manager, category_code):
    """Returns a product package based on type of storage.

    :param manager: The storage manager which calls this function.
    :param category_code: Category code of product package.
    :return: Returns a packaged based on type of storage.
    """

    _filter = utils.NestedDict({})
    _filter['categories']['categoryCode'] = (
        utils.query_filter(category_code))
    _filter['statusCode'] = (utils.query_filter('ACTIVE'))

    packages = manager.client.call(
        'Product_Package', 'getAllObjects',
        filter=_filter.to_dict(),
        mask='id,name,items[prices[categories],attributes]'
    )
    if len(packages) == 0:
        raise ValueError('No packages were found for %s' % category_code)
    if len(packages) > 1:
        raise ValueError('More than one package was found for %s'
                         % category_code)

    return packages[0]


def get_location_id(manager, location):
    """Returns location id

    :param manager: The storage manager which calls this function.
    :param location: Datacenter short name
    :return: Returns location id
    """
    loc_svc = manager.client['Location_Datacenter']
    datacenters = loc_svc.getDatacenters(mask='mask[longName,id,name]')
    for datacenter in datacenters:
        if datacenter['name'] == location:
            location = datacenter['id']
            return location
    raise ValueError('Invalid datacenter name specified.')


def find_price_by_category(package, price_category):
    """Find the price in the given package that has the specified category

    :param package: The AsAService, Enterprise, or Performance product package
    :param price_category: The price category code to search for
    :return: Returns the price for the given category, or an error if not found
    """
    for item in package['items']:
        price_id = _find_price_id(item['prices'], price_category)
        if price_id:
            return price_id

    raise ValueError("Could not find price with the category, %s" % price_category)


def find_ent_space_price(package, category, size, tier_level):
    """Find the space price for the given category, size, and tier

    :param package: The Enterprise (Endurance) product package
    :param category: The category of space (endurance, replication, snapshot)
    :param size: The size for which a price is desired
    :param tier_level: The endurance tier for which a price is desired
    :return: Returns the matching price, or an error if not found
    """
    if category == 'snapshot':
        category_code = 'storage_snapshot_space'
    elif category == 'replication':
        category_code = 'performance_storage_replication'
    else:  # category == 'endurance'
        category_code = 'performance_storage_space'

    level = ENDURANCE_TIERS.get(tier_level)

    for item in package['items']:
        if int(item['capacity']) != size:
            continue
        price_id = _find_price_id(item['prices'], category_code, 'STORAGE_TIER_LEVEL', level)
        if price_id:
            return price_id

    raise ValueError("Could not find price for %s storage space" % category)


def find_ent_endurance_tier_price(package, tier_level):
    """Find the price in the given package with the specified tier level

    :param package: The Enterprise (Endurance) product package
    :param tier_level: The endurance tier for which a price is desired
    :return: Returns the price for the given tier, or an error if not found
    """
    for item in package['items']:
        for attribute in item.get('attributes', []):
            if int(attribute['value']) == ENDURANCE_TIERS.get(tier_level):
                break
        else:
            continue

        price_id = _find_price_id(item['prices'], 'storage_tier_level')
        if price_id:
            return price_id

    raise ValueError("Could not find price for endurance tier level")


def find_endurance_tier_iops_per_gb(volume):
    """Find the tier for the given endurance volume (IOPS per GB)

    :param volume: The volume for which the tier level is desired
    :return: Returns a float value indicating the IOPS per GB for the volume
    """
    tier = volume['storageTierLevel']
    iops_per_gb = 0.25

    if tier == "LOW_INTENSITY_TIER":
        iops_per_gb = 0.25
    elif tier == "READHEAVY_TIER":
        iops_per_gb = 2
    elif tier == "WRITEHEAVY_TIER":
        iops_per_gb = 4
    elif tier == "10_IOPS_PER_GB":
        iops_per_gb = 10
    else:
        raise ValueError("Could not find tier IOPS per GB for this volume")

    return iops_per_gb


def find_perf_space_price(package, size):
    """Find the price in the given package with the specified size

    :param package: The Performance product package
    :param size: The storage space size for which a price is desired
    :return: Returns the price for the given size, or an error if not found
    """
    for item in package['items']:
        if int(item['capacity']) != size:
            continue

        price_id = _find_price_id(item['prices'], 'performance_storage_space')
        if price_id:
            return price_id

    raise ValueError("Could not find performance space price for this volume")


def find_perf_iops_price(package, size, iops):
    """Find the price in the given package with the specified size and iops

    :param package: The Performance product package
    :param size: The size of storage space for which an IOPS price is desired
    :param iops: The number of IOPS for which a price is desired
    :return: Returns the price for the size and IOPS, or an error if not found
    """
    for item in package['items']:
        if int(item['capacity']) != int(iops):
            continue

        price_id = _find_price_id(item['prices'], 'performance_storage_iops', 'STORAGE_SPACE', size)
        if price_id:
            return price_id

    raise ValueError("Could not find price for iops for the given volume")


def find_saas_endurance_space_price(package, size, tier_level):
    """Find the SaaS endurance storage space price for the size and tier

    :param package: The Storage As A Service product package
    :param size: The volume size for which a price is desired
    :param tier_level: The endurance tier for which a price is desired
    :return: Returns the price for the size and tier, or an error if not found
    """
    if tier_level != 0.25:
        tier_level = int(tier_level)
    key_name = 'STORAGE_SPACE_FOR_{0}_IOPS_PER_GB'.format(tier_level)
    key_name = key_name.replace(".", "_")
    for item in package['items']:
        if item['keyName'] != key_name:
            continue

        if 'capacityMinimum' not in item or 'capacityMaximum' not in item:
            continue

        capacity_minimum = int(item['capacityMinimum'])
        capacity_maximum = int(item['capacityMaximum'])
        if size < capacity_minimum or size > capacity_maximum:
            continue

        price_id = _find_price_id(item['prices'], 'performance_storage_space')
        if price_id:
            return price_id

    raise ValueError("Could not find price for endurance storage space")


def find_saas_endurance_tier_price(package, tier_level):
    """Find the SaaS storage tier level price for the specified tier level

    :param package: The Storage As A Service product package
    :param tier_level: The endurance tier for which a price is desired
    :return: Returns the price for the given tier, or an error if not found
    """
    target_capacity = ENDURANCE_TIERS.get(tier_level)
    for item in package['items']:
        if 'itemCategory' not in item\
                or 'categoryCode' not in item['itemCategory']\
                or item['itemCategory']['categoryCode']\
                != 'storage_tier_level':
            continue

        if int(item['capacity']) != target_capacity:
            continue

        price_id = _find_price_id(item['prices'], 'storage_tier_level')
        if price_id:
            return price_id

    raise ValueError("Could not find price for endurance tier level")


def find_saas_perform_space_price(package, size):
    """Find the SaaS performance storage space price for the given size

    :param package: The Storage As A Service product package
    :param size: The volume size for which a price is desired
    :return: Returns the price for the size and tier, or an error if not found
    """
    for item in package['items']:
        if 'itemCategory' not in item\
                or 'categoryCode' not in item['itemCategory']\
                or item['itemCategory']['categoryCode']\
                != 'performance_storage_space':
            continue

        if 'capacityMinimum' not in item or 'capacityMaximum' not in item:
            continue

        capacity_minimum = int(item['capacityMinimum'])
        capacity_maximum = int(item['capacityMaximum'])
        if size < capacity_minimum or size > capacity_maximum:
            continue

        key_name = '{0}_{1}_GBS'.format(capacity_minimum, capacity_maximum)
        if item['keyName'] != key_name:
            continue
        price_id = _find_price_id(item['prices'], 'performance_storage_space')
        if price_id:
            return price_id

    raise ValueError("Could not find price for performance storage space")


def find_saas_perform_iops_price(package, size, iops):
    """Find the SaaS IOPS price for the specified size and iops

    :param package: The Storage As A Service product package
    :param size: The volume size for which a price is desired
    :param iops: The number of IOPS for which a price is desired
    :return: Returns the price for the size and IOPS, or an error if not found
    """
    for item in package['items']:
        if 'itemCategory' not in item\
                or 'categoryCode' not in item['itemCategory']\
                or item['itemCategory']['categoryCode']\
                != 'performance_storage_iops':
            continue

        if 'capacityMinimum' not in item or 'capacityMaximum' not in item:
            continue

        capacity_minimum = int(item['capacityMinimum'])
        capacity_maximum = int(item['capacityMaximum'])
        if iops < capacity_minimum or iops > capacity_maximum:
            continue

        price_id = _find_price_id(item['prices'], 'performance_storage_iops', 'STORAGE_SPACE', size)
        if price_id:
            return price_id

    raise ValueError("Could not find price for iops for the given volume")


def find_saas_snapshot_space_price(package, size, tier=None, iops=None):
    """Find the price in the SaaS package for the desired snapshot space size

    :param package: The product package of the endurance storage type
    :param size: The snapshot space size for which a price is desired
    :param tier: The tier of the volume for which space is being ordered
    :param iops: The IOPS of the volume for which space is being ordered
    :return: Returns the price for the given size, or an error if not found
    """
    if tier is not None:
        target_value = ENDURANCE_TIERS.get(tier)
        target_restriction_type = 'STORAGE_TIER_LEVEL'
    else:
        target_value = iops
        target_restriction_type = 'IOPS'

    for item in package['items']:
        if int(item['capacity']) != size:
            continue

        price_id = _find_price_id(item['prices'], 'storage_snapshot_space', target_restriction_type, target_value)
        if price_id:
            return price_id

    raise ValueError("Could not find price for snapshot space")


def find_saas_replication_price(package, tier=None, iops=None):
    """Find the price in the given package for the desired replicant volume

    :param package: The product package of the endurance storage type
    :param tier: The tier of the primary storage volume
    :param iops: The IOPS of the primary storage volume
    :return: Returns the replication price, or an error if not found
    """
    if tier is not None:
        target_value = ENDURANCE_TIERS.get(tier)
        target_item_keyname = 'REPLICATION_FOR_TIERBASED_PERFORMANCE'
        target_restriction_type = 'STORAGE_TIER_LEVEL'
    else:
        target_value = iops
        target_item_keyname = 'REPLICATION_FOR_IOPSBASED_PERFORMANCE'
        target_restriction_type = 'IOPS'

    for item in package['items']:
        if item['keyName'] != target_item_keyname:
            continue

        price_id = _find_price_id(
            item['prices'],
            'performance_storage_replication',
            target_restriction_type,
            target_value
        )
        if price_id:
            return price_id

    raise ValueError("Could not find price for replicant volume")


def find_snapshot_schedule_id(volume, snapshot_schedule_keyname):
    """Find the snapshot schedule ID for the given volume and keyname

    :param volume: The volume for which the snapshot ID is desired
    :param snapshot_schedule_keyname: The keyname of the snapshot schedule
    :return: Returns an int value indicating the volume's snapshot schedule ID
    """
    for schedule in volume['schedules']:
        if 'type' in schedule and 'keyname' in schedule['type']:
            if schedule['type']['keyname'] == snapshot_schedule_keyname:
                return schedule['id']

    raise ValueError("The given snapshot schedule ID was not found for "
                     "the given storage volume")


def prepare_snapshot_order_object(manager, volume, capacity, tier, upgrade):
    """Prepare the snapshot space order object for the placeOrder() method

    :param manager: The File or Block manager calling this function
    :param integer volume: The volume for which snapshot space is ordered
    :param integer capacity: The snapshot space size to order, in GB
    :param float tier: The tier level of the volume, in IOPS per GB (optional)
    :param boolean upgrade: Flag to indicate if this order is an upgrade
    :return: Returns the order object for the
             Product_Order service's placeOrder() method
    """
    # Ensure the storage volume has not been cancelled
    if 'billingItem' not in volume:
        raise exceptions.SoftLayerError(
            'This volume has been cancelled; unable to order snapshot space')

    # Determine and validate the storage volume's billing item category
    billing_item_category_code = volume['billingItem']['categoryCode']
    if billing_item_category_code == 'storage_as_a_service':
        order_type_is_saas = True
    elif billing_item_category_code == 'storage_service_enterprise':
        order_type_is_saas = False
    else:
        raise exceptions.SoftLayerError(
            "Snapshot space cannot be ordered for a primary volume with a "
            "billing item category code of '%s'" % billing_item_category_code)

    # Use the volume's billing item category code to get the product package
    package = get_package(manager, billing_item_category_code)

    # Find prices based on the volume's type and billing item category
    if order_type_is_saas:  # 'storage_as_a_service' package
        volume_storage_type = volume['storageType']['keyName']
        if 'ENDURANCE' in volume_storage_type:
            if tier is None:
                tier = find_endurance_tier_iops_per_gb(volume)
            prices = [find_saas_snapshot_space_price(
                package, capacity, tier=tier)]
        elif 'PERFORMANCE' in volume_storage_type:
            if not _staas_version_is_v2_or_above(volume):
                raise exceptions.SoftLayerError(
                    "Snapshot space cannot be ordered for this performance "
                    "volume since it does not support Encryption at Rest.")
            iops = int(volume['provisionedIops'])
            prices = [find_saas_snapshot_space_price(
                package, capacity, iops=iops)]
        else:
            raise exceptions.SoftLayerError(
                "Storage volume does not have a valid storage type "
                "(with an appropriate keyName to indicate the "
                "volume is a PERFORMANCE or an ENDURANCE volume)")
    else:  # 'storage_service_enterprise' package
        if tier is None:
            tier = find_endurance_tier_iops_per_gb(volume)
        prices = [find_ent_space_price(package, 'snapshot', capacity, tier)]

    # Currently, these types are valid for snapshot space orders, whether
    # the base volume's order container was Enterprise or AsAService
    if upgrade:
        complex_type = 'SoftLayer_Container_Product_Order_'\
                       'Network_Storage_Enterprise_SnapshotSpace_Upgrade'
    else:
        complex_type = 'SoftLayer_Container_Product_Order_'\
                       'Network_Storage_Enterprise_SnapshotSpace'

    # Determine if hourly billing should be used
    hourly_billing_flag = utils.lookup(volume, 'billingItem', 'hourlyFlag')
    if hourly_billing_flag is None:
        hourly_billing_flag = False

    # Build and return the order object
    snapshot_space_order = {
        'complexType': complex_type,
        'packageId': package['id'],
        'prices': prices,
        'quantity': 1,
        'location': volume['billingItem']['location']['id'],
        'volumeId': volume['id'],
        'useHourlyPricing': hourly_billing_flag
    }

    return snapshot_space_order


def prepare_volume_order_object(manager, storage_type, location, size,
                                iops, tier, snapshot_size, service_offering,
                                volume_type, hourly_billing_flag=False):
    """Prepare the order object which is submitted to the placeOrder() method

    :param manager: The File or Block manager calling this function
    :param storage_type: "performance" or "endurance"
    :param location: Requested datacenter location name for the ordered volume
    :param size: Desired size of the volume, in GB
    :param iops: Number of IOPs for a "Performance" volume order
    :param tier: Tier level to use for an "Endurance" volume order
    :param snapshot_size: The size of snapshot space for the volume (optional)
    :param service_offering: Requested offering package to use for the order
    :param volume_type: The type of the volume to order ('file' or 'block')
    :param hourly_billing_flag: Billing type, monthly (False) or hourly (True)
    :return: Returns the order object for the
             Product_Order service's placeOrder() method
    """
    # Ensure the volume storage type is valid
    if storage_type != 'performance' and storage_type != 'endurance':
        raise exceptions.SoftLayerError(
            "Volume storage type must be either performance or endurance")

    # Find the ID for the requested location
    try:
        location_id = get_location_id(manager, location)
    except ValueError:
        raise exceptions.SoftLayerError(
            "Invalid datacenter name specified. "
            "Please provide the lower case short name (e.g.: dal09)")

    # Determine the category code to use for the order (and product package)
    order_type_is_saas, order_category_code = _get_order_type_and_category(
        service_offering,
        storage_type,
        volume_type
    )

    # Get the product package for the given category code
    package = get_package(manager, order_category_code)

    # Based on the storage type and product package, build up the complex type
    # and array of price codes to include in the order object
    base_type_name = 'SoftLayer_Container_Product_Order_Network_'
    if order_type_is_saas:
        complex_type = base_type_name + 'Storage_AsAService'
        if storage_type == 'performance':
            prices = [
                find_price_by_category(package, order_category_code),
                find_price_by_category(package, 'storage_' + volume_type),
                find_saas_perform_space_price(package, size),
                find_saas_perform_iops_price(package, size, iops)
            ]
            if snapshot_size is not None:
                prices.append(find_saas_snapshot_space_price(
                    package, snapshot_size, iops=iops))
        else:  # storage_type == 'endurance'
            prices = [
                find_price_by_category(package, order_category_code),
                find_price_by_category(package, 'storage_' + volume_type),
                find_saas_endurance_space_price(package, size, tier),
                find_saas_endurance_tier_price(package, tier)
            ]
            if snapshot_size is not None:
                prices.append(find_saas_snapshot_space_price(
                    package, snapshot_size, tier=tier))
    else:  # offering package is enterprise or performance
        if storage_type == 'performance':
            if volume_type == 'block':
                complex_type = base_type_name + 'PerformanceStorage_Iscsi'
            else:
                complex_type = base_type_name + 'PerformanceStorage_Nfs'
            prices = [
                find_price_by_category(package, order_category_code),
                find_perf_space_price(package, size),
                find_perf_iops_price(package, size, iops),
            ]
        else:  # storage_type == 'endurance'
            complex_type = base_type_name + 'Storage_Enterprise'
            prices = [
                find_price_by_category(package, order_category_code),
                find_price_by_category(package, 'storage_' + volume_type),
                find_ent_space_price(package, 'endurance', size, tier),
                find_ent_endurance_tier_price(package, tier),
            ]
            if snapshot_size is not None:
                prices.append(find_ent_space_price(
                    package, 'snapshot', snapshot_size, tier))

    # Build and return the order object
    order = {
        'complexType': complex_type,
        'packageId': package['id'],
        'prices': prices,
        'quantity': 1,
        'location': location_id,
        'useHourlyPricing': hourly_billing_flag
    }

    if order_type_is_saas:
        order['volumeSize'] = size
        if storage_type == 'performance':
            order['iops'] = iops

    return order


def _get_order_type_and_category(service_offering, storage_type, volume_type):
    if service_offering == 'storage_as_a_service':
        order_type_is_saas = True
        order_category_code = 'storage_as_a_service'
    elif service_offering == 'enterprise':
        order_type_is_saas = False
        if storage_type == 'endurance':
            order_category_code = 'storage_service_enterprise'
        else:
            raise exceptions.SoftLayerError(
                "The requested offering package, '%s', is not available for "
                "the '%s' storage type." % (service_offering, storage_type))
    elif service_offering == 'performance':
        order_type_is_saas = False
        if storage_type == 'performance':
            if volume_type == 'block':
                order_category_code = 'performance_storage_iscsi'
            else:
                order_category_code = 'performance_storage_nfs'
        else:
            raise exceptions.SoftLayerError(
                "The requested offering package, '%s', is not available for "
                "the '%s' storage type." % (service_offering, storage_type))
    else:
        raise exceptions.SoftLayerError(
            "The requested service offering package is not valid. "
            "Please check the available options and try again.")

    return order_type_is_saas, order_category_code


def prepare_replicant_order_object(manager, snapshot_schedule, location,
                                   tier, volume, volume_type):
    """Prepare the order object which is submitted to the placeOrder() method

    :param manager: The File or Block manager calling this function
    :param snapshot_schedule: The primary volume's snapshot
                              schedule to use for replication
    :param location: The location for the ordered replicant volume
    :param tier: The tier (IOPS per GB) of the primary volume
    :param volume: The primary volume as a SoftLayer_Network_Storage object
    :param volume_type: The type of the primary volume ('file' or 'block')
    :return: Returns the order object for the
             Product_Order service's placeOrder() method
    """
    # Ensure the primary volume and snapshot space are not set for cancellation
    if 'billingItem' not in volume\
            or volume['billingItem']['cancellationDate'] != '':
        raise exceptions.SoftLayerError(
            'This volume is set for cancellation; '
            'unable to order replicant volume')

    for child in volume['billingItem']['activeChildren']:
        if child['categoryCode'] == 'storage_snapshot_space'\
                and child['cancellationDate'] != '':
            raise exceptions.SoftLayerError(
                'The snapshot space for this volume is set for '
                'cancellation; unable to order replicant volume')

    # Find the ID for the requested location
    try:
        location_id = get_location_id(manager, location)
    except ValueError:
        raise exceptions.SoftLayerError(
            "Invalid datacenter name specified. "
            "Please provide the lower case short name (e.g.: dal09)")

    # Get sizes and properties needed for the order
    volume_size = int(volume['capacityGb'])

    billing_item_category_code = volume['billingItem']['categoryCode']
    if billing_item_category_code == 'storage_as_a_service':
        order_type_is_saas = True
    elif billing_item_category_code == 'storage_service_enterprise':
        order_type_is_saas = False
    else:
        raise exceptions.SoftLayerError(
            "A replicant volume cannot be ordered for a primary volume with a "
            "billing item category code of '%s'" % billing_item_category_code)

    if 'snapshotCapacityGb' in volume:
        snapshot_size = int(volume['snapshotCapacityGb'])
    else:
        raise exceptions.SoftLayerError(
            "Snapshot capacity not found for the given primary volume")

    snapshot_schedule_id = find_snapshot_schedule_id(
        volume,
        'SNAPSHOT_' + snapshot_schedule
    )

    # Use the volume's billing item category code to get the product package
    package = get_package(manager, billing_item_category_code)

    # Find prices based on the primary volume's type and billing item category
    if order_type_is_saas:  # 'storage_as_a_service' package
        complex_type = 'SoftLayer_Container_Product_Order_'\
                       'Network_Storage_AsAService'
        volume_storage_type = volume['storageType']['keyName']
        if 'ENDURANCE' in volume_storage_type:
            volume_is_performance = False
            if tier is None:
                tier = find_endurance_tier_iops_per_gb(volume)
            prices = [
                find_price_by_category(package, billing_item_category_code),
                find_price_by_category(package, 'storage_' + volume_type),
                find_saas_endurance_space_price(package, volume_size, tier),
                find_saas_endurance_tier_price(package, tier),
                find_saas_snapshot_space_price(
                    package, snapshot_size, tier=tier),
                find_saas_replication_price(package, tier=tier)
            ]
        elif 'PERFORMANCE' in volume_storage_type:
            if not _staas_version_is_v2_or_above(volume):
                raise exceptions.SoftLayerError(
                    "A replica volume cannot be ordered for this performance "
                    "volume since it does not support Encryption at Rest.")
            volume_is_performance = True
            iops = int(volume['provisionedIops'])
            prices = [
                find_price_by_category(package, billing_item_category_code),
                find_price_by_category(package, 'storage_' + volume_type),
                find_saas_perform_space_price(package, volume_size),
                find_saas_perform_iops_price(package, volume_size, iops),
                find_saas_snapshot_space_price(
                    package, snapshot_size, iops=iops),
                find_saas_replication_price(package, iops=iops)
            ]
        else:
            raise exceptions.SoftLayerError(
                "Storage volume does not have a valid storage type "
                "(with an appropriate keyName to indicate the "
                "volume is a PERFORMANCE or an ENDURANCE volume)")
    else:  # 'storage_service_enterprise' package
        complex_type = 'SoftLayer_Container_Product_Order_'\
                       'Network_Storage_Enterprise'
        volume_is_performance = False
        if tier is None:
            tier = find_endurance_tier_iops_per_gb(volume)
        prices = [
            find_price_by_category(package, billing_item_category_code),
            find_price_by_category(package, 'storage_' + volume_type),
            find_ent_space_price(package, 'endurance', volume_size, tier),
            find_ent_endurance_tier_price(package, tier),
            find_ent_space_price(package, 'snapshot', snapshot_size, tier),
            find_ent_space_price(package, 'replication', volume_size, tier)
        ]

    # Determine if hourly billing should be used
    hourly_billing_flag = utils.lookup(volume, 'billingItem', 'hourlyFlag')
    if hourly_billing_flag is None:
        hourly_billing_flag = False

    # Build and return the order object
    replicant_order = {
        'complexType': complex_type,
        'packageId': package['id'],
        'prices': prices,
        'quantity': 1,
        'location': location_id,
        'originVolumeId': volume['id'],
        'originVolumeScheduleId': snapshot_schedule_id,
        'useHourlyPricing': hourly_billing_flag
    }

    if order_type_is_saas:
        replicant_order['volumeSize'] = volume_size
        if volume_is_performance:
            replicant_order['iops'] = iops

    return replicant_order


def prepare_duplicate_order_object(manager, origin_volume, iops, tier,
                                   duplicate_size, duplicate_snapshot_size,
                                   volume_type, hourly_billing_flag=False):
    """Prepare the duplicate order to submit to SoftLayer_Product::placeOrder()

    :param manager: The File or Block manager calling this function
    :param origin_volume: The origin volume which is being duplicated
    :param iops: The IOPS for the duplicate volume (performance)
    :param tier: The tier level for the duplicate volume (endurance)
    :param duplicate_size: The requested size for the duplicate volume
    :param duplicate_snapshot_size: The size for the duplicate snapshot space
    :param volume_type: The type of the origin volume ('file' or 'block')
    :param hourly_billing_flag: Billing type, monthly (False) or hourly (True)
    :return: Returns the order object to be passed to the
             placeOrder() method of the Product_Order service
    """

    # Verify that the origin volume has not been cancelled
    if 'billingItem' not in origin_volume:
        raise exceptions.SoftLayerError(
            "The origin volume has been cancelled; "
            "unable to order duplicate volume")

    # Verify that the origin volume has snapshot space (needed for duplication)
    if isinstance(utils.lookup(origin_volume, 'snapshotCapacityGb'), str):
        origin_snapshot_size = int(origin_volume['snapshotCapacityGb'])
    else:
        raise exceptions.SoftLayerError(
            "Snapshot space not found for the origin volume. "
            "Origin snapshot space is needed for duplication.")

    # Obtain the datacenter location ID for the duplicate
    if isinstance(utils.lookup(origin_volume, 'billingItem',
                               'location', 'id'), int):
        location_id = origin_volume['billingItem']['location']['id']
    else:
        raise exceptions.SoftLayerError(
            "Cannot find origin volume's location")

    # Ensure the origin volume is STaaS v2 or higher
    # and supports Encryption at Rest
    if not _staas_version_is_v2_or_above(origin_volume):
        raise exceptions.SoftLayerError(
            "This volume cannot be duplicated since it "
            "does not support Encryption at Rest.")

    # If no specific snapshot space was requested for the duplicate,
    # use the origin snapshot space size
    if duplicate_snapshot_size is None:
        duplicate_snapshot_size = origin_snapshot_size

    # Use the origin volume size if no size was specified for the duplicate
    if duplicate_size is None:
        duplicate_size = origin_volume['capacityGb']

    # Get the appropriate package for the order
    # ('storage_as_a_service' is currently used for duplicate volumes)
    package = get_package(manager, 'storage_as_a_service')

    # Determine the IOPS or tier level for the duplicate volume, along with
    # the type and prices for the order
    origin_storage_type = origin_volume['storageType']['keyName']
    if 'PERFORMANCE' in origin_storage_type:
        volume_is_performance = True
        if iops is None:
            iops = int(origin_volume.get('provisionedIops', 0))
            if iops <= 0:
                raise exceptions.SoftLayerError("Cannot find origin volume's provisioned IOPS")
        # Set up the price array for the order
        prices = [
            find_price_by_category(package, 'storage_as_a_service'),
            find_price_by_category(package, 'storage_' + volume_type),
            find_saas_perform_space_price(package, duplicate_size),
            find_saas_perform_iops_price(package, duplicate_size, iops),
        ]
        # Add the price code for snapshot space as well, unless 0 GB was given
        if duplicate_snapshot_size > 0:
            prices.append(find_saas_snapshot_space_price(
                package, duplicate_snapshot_size, iops=iops))

    elif 'ENDURANCE' in origin_storage_type:
        volume_is_performance = False
        if tier is None:
            tier = find_endurance_tier_iops_per_gb(origin_volume)
        # Set up the price array for the order
        prices = [
            find_price_by_category(package, 'storage_as_a_service'),
            find_price_by_category(package, 'storage_' + volume_type),
            find_saas_endurance_space_price(package, duplicate_size, tier),
            find_saas_endurance_tier_price(package, tier),
        ]
        # Add the price code for snapshot space as well, unless 0 GB was given
        if duplicate_snapshot_size > 0:
            prices.append(find_saas_snapshot_space_price(
                package, duplicate_snapshot_size, tier=tier))

    else:
        raise exceptions.SoftLayerError(
            "Origin volume does not have a valid storage type "
            "(with an appropriate keyName to indicate the "
            "volume is a PERFORMANCE or an ENDURANCE volume)")

    duplicate_order = {
        'complexType': 'SoftLayer_Container_Product_Order_'
                       'Network_Storage_AsAService',
        'packageId': package['id'],
        'prices': prices,
        'volumeSize': duplicate_size,
        'quantity': 1,
        'location': location_id,
        'duplicateOriginVolumeId': origin_volume['id'],
        'useHourlyPricing': hourly_billing_flag
    }

    if volume_is_performance:
        duplicate_order['iops'] = iops

    return duplicate_order


def prepare_modify_order_object(manager, volume, new_iops, new_tier, new_size):
    """Prepare the modification order to submit to SoftLayer_Product::placeOrder()

    :param manager: The File or Block manager calling this function
    :param volume: The volume which is being modified
    :param new_iops: The new IOPS for the volume (performance)
    :param new_tier: The new tier level for the volume (endurance)
    :param new_size: The requested new size for the volume
    :return: Returns the order object to be passed to the placeOrder() method of the Product_Order service
    """

    # Verify that the origin volume has not been cancelled
    if 'billingItem' not in volume:
        raise exceptions.SoftLayerError("The volume has been cancelled; unable to modify volume.")

    # Ensure the origin volume is STaaS v2 or higher and supports Encryption at Rest
    if not _staas_version_is_v2_or_above(volume):
        raise exceptions.SoftLayerError("This volume cannot be modified since it does not support Encryption at Rest.")

    # Get the appropriate package for the order ('storage_as_a_service' is currently used for modifying volumes)
    package = get_package(manager, 'storage_as_a_service')

    # Based on volume storage type, ensure at least one volume property is being modified,
    # use current values if some are not specified, and lookup price codes for the order
    volume_storage_type = volume['storageType']['keyName']
    if 'PERFORMANCE' in volume_storage_type:
        volume_is_performance = True
        if new_size is None and new_iops is None:
            raise exceptions.SoftLayerError("A size or IOPS value must be given to modify this performance volume.")

        if new_size is None:
            new_size = volume['capacityGb']
        elif new_iops is None:
            new_iops = int(volume.get('provisionedIops', 0))
            if new_iops <= 0:
                raise exceptions.SoftLayerError("Cannot find volume's provisioned IOPS.")

        # Set up the prices array for the order
        prices = [
            find_price_by_category(package, 'storage_as_a_service'),
            find_saas_perform_space_price(package, new_size),
            find_saas_perform_iops_price(package, new_size, new_iops),
        ]

    elif 'ENDURANCE' in volume_storage_type:
        volume_is_performance = False
        if new_size is None and new_tier is None:
            raise exceptions.SoftLayerError("A size or tier value must be given to modify this endurance volume.")

        if new_size is None:
            new_size = volume['capacityGb']
        elif new_tier is None:
            new_tier = find_endurance_tier_iops_per_gb(volume)

        # Set up the prices array for the order
        prices = [
            find_price_by_category(package, 'storage_as_a_service'),
            find_saas_endurance_space_price(package, new_size, new_tier),
            find_saas_endurance_tier_price(package, new_tier),
        ]

    else:
        raise exceptions.SoftLayerError("Volume does not have a valid storage type (with an appropriate "
                                        "keyName to indicate the volume is a PERFORMANCE or an ENDURANCE volume).")

    modify_order = {
        'complexType': 'SoftLayer_Container_Product_Order_Network_Storage_AsAService_Upgrade',
        'packageId': package['id'],
        'prices': prices,
        'volume': {'id': volume['id']},
        'volumeSize': new_size
    }

    if volume_is_performance:
        modify_order['iops'] = new_iops

    return modify_order


def _has_category(categories, category_code):
    return any(
        True
        for category
        in categories
        if category['categoryCode'] == category_code
    )


def _staas_version_is_v2_or_above(volume):
    return int(volume['staasVersion']) > 1 and volume['hasEncryptionAtRest']


def _find_price_id(prices, category, restriction_type=None, restriction_value=None):
    for price in prices:
        # Only collect prices from valid location groups.
        if price['locationGroupId']:
            continue

        if restriction_type is not None and restriction_value is not None:
            if restriction_type != price['capacityRestrictionType']\
                    or restriction_value < int(price['capacityRestrictionMinimum'])\
                    or restriction_value > int(price['capacityRestrictionMaximum']):
                continue

        if not _has_category(price['categories'], category):
            continue

        return {'id': price['id']}
