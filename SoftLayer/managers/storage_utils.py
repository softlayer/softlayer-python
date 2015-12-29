"""
    SoftLayer.storage_utils
    ~~~~~~~~~~~~~~~
    Utility functions used by File and Block Storage Managers

    :license: MIT, see LICENSE for more details.
"""
from SoftLayer import utils


ENDURANCE_TIERS = {
    0.25: 100,
    2: 200,
    4: 300,
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
    """Returns a product packaged based on type of storage.

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
    tier_description_split = volume['storageTierLevel']['description'].split()

    if tier_description_split != []:
        iops_per_gb = tier_description_split[0]

        if iops_per_gb == '0.25':
            return 0.25

        if iops_per_gb == '2':
            return 2.0

        if iops_per_gb == '4':
            return 4.0

    raise ValueError("Could not find tier IOPS per GB for this volume")


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


def _has_category(categories, category_code):
    return any(
        True
        for category
        in categories
        if category['categoryCode'] == category_code
    )
