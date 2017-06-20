"""
    SoftLayer.storage_utils
    ~~~~~~~~~~~~~~~
    Utility functions used by File and Block Storage Managers

    :license: MIT, see LICENSE for more details.
"""
from SoftLayer import exceptions
from SoftLayer import utils


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


def find_endurance_price(package, price_category):
    """Find the price in the given package that has the specified category

    :param package: The product package of the endurance storage type
    :param price_category: The price category to search for
    :return: Returns the price for the given category, or an error if not found
    """
    for item in package['items']:
        for price in item['prices']:
            # Only collect prices from valid location groups.
            if price['locationGroupId'] != '':
                continue

            if not _has_category(price['categories'], price_category):
                continue

            return price

    raise ValueError("Could not find price for endurance storage")


def find_endurance_space_price(package, size, tier_level):
    """Find the price in the given package with the specified size and tier

    :param package: The product package of the endurance storage type
    :param size: The size for which a price is desired
    :param tier_level: The endurance tier for which a price is desired
    :return: Returns the price for the size and tier, or an error if not found
    """
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


def find_endurance_tier_price(package, tier_level):
    """Find the price in the given package with the specified tier level

    :param package: The product package of the endurance storage type
    :param tier_level: The endurance tier for which a price is desired
    :return: Returns the price for the given tier, or an error if not found
    """
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


def find_performance_price(package, price_category):
    """Find the price in the given package that has the specified category

    :param package: The product package of the performance storage type
    :param price_category: The price category to search for
    :return: Returns the price for the given category, or an error if not found
    """
    for item in package['items']:
        for price in item['prices']:
            # Only collect prices from valid location groups.
            if price['locationGroupId'] != '':
                continue

            if not _has_category(price['categories'], price_category):
                continue

            return price

    raise ValueError("Could not find price for performance storage")


def find_performance_space_price(package, size):
    """Find the price in the given package with the specified size

    :param package: The product package of the performance storage type
    :param size: The size for which a price is desired
    :return: Returns the price for the given size, or an error if not found
    """
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

    raise ValueError("Could not find disk space price for the given volume")


def find_performance_iops_price(package, size, iops):
    """Find the price in the given package with the specified size and iops

    :param package: The product package of the performance storage type
    :param size: The size for which a price is desired
    :param iops: The number of IOPS for which a price is desired
    :return: Returns the price for the size and IOPS, or an error if not found
    """
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

    raise ValueError("Could not find price for iops for the given volume")


def find_replication_price(package, capacity, tier_level):
    """Find the price in the given package for the desired replicant volume

    :param package: The product package of the endurance storage type
    :param capacity: The capacity of the primary storage volume
    :param tier_level: The tier of the primary storage volume
    :return: Returns the price for the given size, or an error if not found
    """
    for item in package['items']:
        if int(item['capacity']) != capacity:
            continue

        for price in item['prices']:
            # Only collect prices from valid location groups.
            if price['locationGroupId'] != '':
                continue

            if not _has_category(price['categories'],
                                 'performance_storage_replication'):
                continue

            level = ENDURANCE_TIERS.get(tier_level)
            if level < int(price['capacityRestrictionMinimum']):
                continue

            if level > int(price['capacityRestrictionMaximum']):
                continue

            return price

    raise ValueError("Could not find price for replicant volume")


def find_snapshot_space_price(package, size, tier_level):
    """Find the price in the given package for the desired snapshot space size

    :param package: The product package of the endurance storage type
    :param size: The snapshot space size for which a price is desired
    :param tier_level: The tier of the volume for which space is being ordered
    :return: Returns the price for the given size, or an error if not found
    """
    for item in package['items']:
        if int(item['capacity']) != size:
            continue

        for price in item['prices']:
            # Only collect prices from valid location groups.
            if price['locationGroupId'] != '':
                continue

            if not _has_category(price['categories'],
                                 'storage_snapshot_space'):
                continue

            level = ENDURANCE_TIERS.get(tier_level)
            if level < int(price['capacityRestrictionMinimum']):
                continue

            if level > int(price['capacityRestrictionMaximum']):
                continue

            return price

    raise ValueError("Could not find price for snapshot space")


def find_saas_price_by_category(package, price_category):
    """Find a price in the SaaS package with the specified category

    :param package: The Storage As A Service product package
    :param price_category: The price category to search for
    :return: Returns a price for the given category, or an error if not found
    """
    for item in package['items']:
        for price in item['prices']:
            if price['locationGroupId'] != '':
                continue

            if not _has_category(price['categories'], price_category):
                continue

            return {'id': price['id']}

    raise ValueError("Could not find price with the category, %s"
                     % price_category)


def find_saas_endurance_space_price(package, size, tier_level):
    """Find the SaaS endurance storage space price for the size and tier

    :param package: The Storage As A Service product package
    :param size: The volume size for which a price is desired
    :param tier_level: The endurance tier for which a price is desired
    :return: Returns the price for the size and tier, or an error if not found
    """
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

        for price in item['prices']:
            # Only collect prices from valid location groups.
            if price['locationGroupId'] != '':
                continue

            if not _has_category(price['categories'],
                                 'performance_storage_space'):
                continue

            return {'id': price['id']}

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

        for price in item['prices']:
            # Only collect prices from valid location groups.
            if price['locationGroupId'] != '':
                continue

            if not _has_category(price['categories'], 'storage_tier_level'):
                continue

            return {'id': price['id']}

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

        for price in item['prices']:
            # Only collect prices from valid location groups.
            if price['locationGroupId'] != '':
                continue

            if not _has_category(price['categories'],
                                 'performance_storage_space'):
                continue

            return {'id': price['id']}

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

        for price in item['prices']:
            # Only collect prices from valid location groups.
            if price['locationGroupId'] != '':
                continue

            if not _has_category(price['categories'],
                                 'performance_storage_iops'):
                continue

            if price['capacityRestrictionType'] != 'STORAGE_SPACE'\
                    or size < int(price['capacityRestrictionMinimum'])\
                    or size > int(price['capacityRestrictionMaximum']):
                continue

            return {'id': price['id']}

    raise ValueError("Could not find price for iops for the given volume")


def find_saas_snapshot_space_price(package, size, tier_level=None, iops=None):
    """Find the price in the SaaS package for the desired snapshot space size

    :param package: The product package of the endurance storage type
    :param size: The snapshot space size for which a price is desired
    :param tier_level: The tier of the volume for which space is being ordered
    :param iops: The IOPS of the volume for which space is being ordered
    :return: Returns the price for the given size, or an error if not found
    """
    if tier_level is not None:
        target_value = ENDURANCE_TIERS.get(tier_level)
        target_restriction_type = 'STORAGE_TIER_LEVEL'
    else:
        target_value = iops
        target_restriction_type = 'IOPS'

    for item in package['items']:
        if int(item['capacity']) != size:
            continue

        for price in item['prices']:
            # Only collect prices from valid location groups.
            if price['locationGroupId'] != '':
                continue

            if target_restriction_type != price['capacityRestrictionType']\
                    or target_value < int(price['capacityRestrictionMinimum'])\
                    or target_value > int(price['capacityRestrictionMaximum']):
                continue

            if not _has_category(price['categories'],
                                 'storage_snapshot_space'):
                continue

            return {'id': price['id']}

    raise ValueError("Could not find price for snapshot space")


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


def prepare_replicant_order_object(manager, volume_id, snapshot_schedule,
                                   location, tier, volume, volume_type):
    """Prepare the order object which is submitted to the placeOrder() method

    :param manager: The File or Block manager calling this function
    :param volume_id: The ID of the primary volume to be replicated
    :param snapshot_schedule: The primary volume's snapshot
                              schedule to use for replication
    :param location: The location for the ordered replicant volume
    :param tier: The tier (IOPS per GB) of the primary volume
    :param volume: The primary volume as a SoftLayer_Network_Storage object
    :param volume_type: The type of the primary volume ('file' or 'block')
    :return: Returns the order object for the
             Product_Order service's placeOrder() method
    """

    try:
        location_id = get_location_id(manager, location)
    except ValueError:
        raise exceptions.SoftLayerError(
            "Invalid data center name specified. "
            "Please provide the lower case short name (e.g.: dal09)")

    volume_capacity = int(volume['capacityGb'])
    storage_type = volume['billingItem']['categoryCode']

    if storage_type != 'storage_service_enterprise':
        raise exceptions.SoftLayerError(
            "Primary volume storage_type must be Endurance")

    if 'snapshotCapacityGb' in volume:
        volume_snapshot_capacity = int(volume['snapshotCapacityGb'])
    else:
        raise exceptions.SoftLayerError(
            "Snapshot capacity not found for the given primary volume")

    snapshot_schedule_id = find_snapshot_schedule_id(
        volume,
        'SNAPSHOT_' + snapshot_schedule
    )

    if volume['billingItem']['cancellationDate'] != '':
        raise exceptions.SoftLayerError(
            'This volume is set for cancellation; '
            'unable to order replicant volume')

    for child in volume['billingItem']['activeChildren']:
        if child['categoryCode'] == 'storage_snapshot_space'\
                and child['cancellationDate'] != '':
            raise exceptions.SoftLayerError(
                'The snapshot space for this volume is set for '
                'cancellation; unable to order replicant volume')

    if tier is None:
        tier = find_endurance_tier_iops_per_gb(volume)

    package = get_package(manager, storage_type)
    prices = [
        find_endurance_price(package, 'storage_service_enterprise'),
        find_endurance_price(package, 'storage_' + volume_type),
        find_endurance_tier_price(package, tier),
        find_endurance_space_price(package, volume_capacity, tier),
        find_snapshot_space_price(package, volume_snapshot_capacity, tier),
        find_replication_price(package, volume_capacity, tier),
    ]

    replicant_order = {
        'complexType': 'SoftLayer_Container_Product_Order_'
                       'Network_Storage_Enterprise',
        'packageId': package['id'],
        'prices': prices,
        'quantity': 1,
        'location': location_id,
        'originVolumeId': int(volume_id),
        'originVolumeScheduleId': snapshot_schedule_id,
    }

    return replicant_order


def prepare_duplicate_order_object(manager, origin_volume, iops, tier,
                                   duplicate_size,
                                   duplicate_snapshot_size, volume_type):
    """Prepare the duplicate order to submit to SoftLayer_Product::placeOrder()

    :param manager: The File or Block manager calling this function
    :param origin_volume: The origin volume which is being duplicated
    :param iops: The IOPS per GB for the duplicant volume (performance)
    :param tier: The tier level for the duplicant volume (endurance)
    :param duplicate_size: The requested size for the duplicate volume
    :param duplicate_snapshot_size: The size for the duplicate snapshot space
    :param volume_type: The type of the origin volume ('file' or 'block')
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

    # If no specific snapshot space was requested for the duplicate,
    # use the origin snapshot space size
    if duplicate_snapshot_size is None:
        duplicate_snapshot_size = origin_snapshot_size

    # Validate the requested duplicate size, and set the size if none was given
    duplicate_size = _validate_duplicate_size(
        origin_volume, duplicate_size, volume_type)

    # Get the appropriate package for the order
    # ('storage_as_a_service' is currently used for duplicate volumes)
    package = get_package(manager, 'storage_as_a_service')

    # Determine the IOPS or tier level for the duplicate volume, along with
    # the type and prices for the order
    origin_storage_type = origin_volume['storageType']['keyName']
    if origin_storage_type == 'PERFORMANCE_BLOCK_STORAGE'\
            or origin_storage_type == 'PERFORMANCE_BLOCK_STORAGE_REPLICANT'\
            or origin_storage_type == 'PERFORMANCE_FILE_STORAGE'\
            or origin_storage_type == 'PERFORMANCE_FILE_STORAGE_REPLICANT':
        volume_is_performance = True
        iops = _validate_dupl_performance_iops(
            origin_volume, iops, duplicate_size)
        # Set up the price array for the order
        prices = [
            find_saas_price_by_category(package, 'storage_as_a_service'),
            find_saas_price_by_category(package, 'storage_' + volume_type),
            find_saas_perform_space_price(package, duplicate_size),
            find_saas_perform_iops_price(package, duplicate_size, iops),
        ]
        # Add the price code for snapshot space as well, unless 0 GB was given
        if duplicate_snapshot_size > 0:
            prices.append(find_saas_snapshot_space_price(
                package, duplicate_snapshot_size, iops=iops))

    elif origin_storage_type == 'ENDURANCE_BLOCK_STORAGE'\
            or origin_storage_type == 'ENDURANCE_BLOCK_STORAGE_REPLICANT'\
            or origin_storage_type == 'ENDURANCE_FILE_STORAGE'\
            or origin_storage_type == 'ENDURANCE_FILE_STORAGE_REPLICANT':
        volume_is_performance = False
        tier = _validate_dupl_endurance_tier(origin_volume, tier)
        # Set up the price array for the order
        prices = [
            find_saas_price_by_category(package, 'storage_as_a_service'),
            find_saas_price_by_category(package, 'storage_' + volume_type),
            find_saas_endurance_space_price(package, duplicate_size, tier),
            find_saas_endurance_tier_price(package, tier),
        ]
        # Add the price code for snapshot space as well, unless 0 GB was given
        if duplicate_snapshot_size > 0:
            prices.append(find_saas_snapshot_space_price(
                package, duplicate_snapshot_size, tier_level=tier))

    else:
        raise exceptions.SoftLayerError(
            "Origin volume does not have a valid storage type "
            "(with an appropriate keyName to indicate the "
            "volume is a PERFORMANCE or ENDURANCE volume)")

    duplicate_order = {
        'complexType': 'SoftLayer_Container_Product_Order_'
                       'Network_Storage_AsAService',
        'packageId': package['id'],
        'prices': prices,
        'volumeSize': duplicate_size,
        'quantity': 1,
        'location': location_id,
        'duplicateOriginVolumeId': origin_volume['id'],
    }

    if volume_is_performance:
        duplicate_order['iops'] = iops

    return duplicate_order


def _validate_duplicate_size(origin_volume, duplicate_volume_size,
                             volume_type):
    # Ensure the origin volume's size is found
    if not isinstance(utils.lookup(origin_volume, 'capacityGb'), int):
        raise exceptions.SoftLayerError("Cannot find origin volume's size.")

    # Determine the volume size/capacity for the duplicate
    if duplicate_volume_size is None:
        duplicate_volume_size = origin_volume['capacityGb']
    # Ensure the duplicate volume size is not below the minimum
    elif duplicate_volume_size < origin_volume['capacityGb']:
        raise exceptions.SoftLayerError(
            "The requested duplicate volume size is too small. Duplicate "
            "volumes must be at least as large as their origin volumes.")

    # Ensure the duplicate volume size is not above the maximum
    if volume_type == 'block':
        # Determine the base size for validating the requested duplicate size
        if 'originalVolumeSize' in origin_volume:
            base_volume_size = int(origin_volume['originalVolumeSize'])
        else:
            base_volume_size = origin_volume['capacityGb']

        # Current limit for block volumes: 10*[origin size]
        if duplicate_volume_size > base_volume_size * 10:
            raise exceptions.SoftLayerError(
                "The requested duplicate volume size is too large. The "
                "maximum size for duplicate block volumes is 10 times the "
                "size of the origin volume or, if the origin volume was also "
                "a duplicate, 10 times the size of the initial origin volume "
                "(i.e. the origin volume from which the first duplicate was "
                "created in the chain of duplicates). "
                "Requested: %s GB. Base origin size: %s GB."
                % (duplicate_volume_size, base_volume_size))

    return duplicate_volume_size


def _validate_dupl_performance_iops(origin_volume, duplicate_iops,
                                    duplicate_size):
    if not isinstance(utils.lookup(origin_volume, 'provisionedIops'), str):
        raise exceptions.SoftLayerError(
            "Cannot find origin volume's provisioned IOPS")

    if duplicate_iops is None:
        duplicate_iops = int(origin_volume['provisionedIops'])
    else:
        origin_iops_per_gb = float(origin_volume['provisionedIops'])\
            / float(origin_volume['capacityGb'])
        duplicate_iops_per_gb = float(duplicate_iops) / float(duplicate_size)
        if origin_iops_per_gb < 0.3 and duplicate_iops_per_gb >= 0.3:
            raise exceptions.SoftLayerError(
                "Origin volume performance is < 0.3 IOPS/GB, "
                "duplicate volume performance must also be < 0.3 "
                "IOPS/GB. %s IOPS/GB (%s/%s) requested."
                % (duplicate_iops_per_gb, duplicate_iops, duplicate_size))
        elif origin_iops_per_gb >= 0.3 and duplicate_iops_per_gb < 0.3:
            raise exceptions.SoftLayerError(
                "Origin volume performance is >= 0.3 IOPS/GB, "
                "duplicate volume performance must also be >= 0.3 "
                "IOPS/GB. %s IOPS/GB (%s/%s) requested."
                % (duplicate_iops_per_gb, duplicate_iops, duplicate_size))
    return duplicate_iops


def _validate_dupl_endurance_tier(origin_volume, duplicate_tier):
    try:
        origin_tier = find_endurance_tier_iops_per_gb(origin_volume)
    except ValueError:
        raise exceptions.SoftLayerError(
            "Cannot find origin volume's tier level")

    if duplicate_tier is None:
        duplicate_tier = origin_tier
    else:
        if duplicate_tier != 0.25:
            duplicate_tier = int(duplicate_tier)

        if origin_tier == 0.25 and duplicate_tier != 0.25:
            raise exceptions.SoftLayerError(
                "Origin volume performance tier is 0.25 IOPS/GB, "
                "duplicate volume performance tier must also be 0.25 "
                "IOPS/GB. %s IOPS/GB requested." % duplicate_tier)
        elif origin_tier != 0.25 and duplicate_tier == 0.25:
            raise exceptions.SoftLayerError(
                "Origin volume performance tier is above 0.25 IOPS/GB, "
                "duplicate volume performance tier must also be above 0.25 "
                "IOPS/GB. %s IOPS/GB requested." % duplicate_tier)
    return duplicate_tier


def _has_category(categories, category_code):
    return any(
        True
        for category
        in categories
        if category['categoryCode'] == category_code
    )
