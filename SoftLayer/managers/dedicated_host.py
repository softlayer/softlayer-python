"""
    SoftLayer.dedicatedhost
    ~~~~~~~~~~~~~~~~~~~~~~~
    DH Manager/helpers

    :license: MIT, see License for more details.
"""

import logging
import SoftLayer

from SoftLayer.managers import ordering
from SoftLayer import utils

# Invalid names are ignored due to long method names and short argument names
# pylint: disable=invalid-name, no-self-use

LOGGER = logging.getLogger(__name__)


class DedicatedHostManager(utils.IdentifierMixin, object):
    """Manages SoftLayer Dedicated Hosts.

        See product information here https://www.ibm.com/cloud/dedicated


    :param SoftLayer.API.BaseClient client: the client instance
    :param SoftLayer.managers.OrderingManager ordering_manager: an optional manager to handle ordering.
                                              If none is provided, one will be auto initialized.
    """

    def __init__(self, client, ordering_manager=None):
        self.client = client
        self.account = client['Account']
        self.host = client['Virtual_DedicatedHost']

        if ordering_manager is None:
            self.ordering_manager = ordering.OrderingManager(client)

    def list_instances(self, tags=None, cpus=None, memory=None, hostname=None,
                       disk=None, datacenter=None, **kwargs):
        """Retrieve a list of all dedicated hosts on the account

        :param list tags: filter based on list of tags
        :param integer cpus: filter based on number of CPUS
        :param integer memory: filter based on amount of memory
        :param string hostname: filter based on hostname
        :param string disk: filter based on disk
        :param string datacenter: filter based on datacenter
        :param dict \\*\\*kwargs: response-level options (mask, limit, etc.)
        :returns: Returns a list of dictionaries representing the matching dedicated host.

        """
        if 'mask' not in kwargs:
            items = [
                'id',
                'name',
                'cpuCount',
                'diskCapacity',
                'memoryCapacity',
                'datacenter',
                'guestCount',
            ]
            kwargs['mask'] = "mask[%s]" % ','.join(items)

        _filter = utils.NestedDict(kwargs.get('filter') or {})
        if tags:
            _filter['dedicatedHosts']['tagReferences']['tag']['name'] = {
                'operation': 'in',
                'options': [{'name': 'data', 'value': tags}],
            }

        if hostname:
            _filter['dedicatedHosts']['name'] = (
                utils.query_filter(hostname)
            )

        if cpus:
            _filter['dedicatedHosts']['cpuCount'] = utils.query_filter(cpus)

        if disk:
            _filter['dedicatedHosts']['diskCapacity'] = (
                utils.query_filter(disk))

        if memory:
            _filter['dedicatedHosts']['memoryCapacity'] = (
                utils.query_filter(memory))

        if datacenter:
            _filter['dedicatedHosts']['datacenter']['name'] = (
                utils.query_filter(datacenter))

        kwargs['filter'] = _filter.to_dict()
        return self.account.getDedicatedHosts(**kwargs)

    def get_host(self, host_id, **kwargs):
        """Get details about a dedicated host.

        :param integer : the host ID
        :returns: A dictionary containing host information.

        Example::

            # Print out host ID 12345.
            dh = mgr.get_host(12345)
            print dh

            # Print out only name and backendRouter for instance 12345
            object_mask = "mask[name,backendRouter[id]]"
            dh = mgr.get_host(12345, mask=mask)
            print dh

        """
        if 'mask' not in kwargs:
            kwargs['mask'] = ('''
                id,
                name,
                cpuCount,
                memoryCapacity,
                diskCapacity,
                createDate,
                modifyDate,
                backendRouter[
                    id,
                    hostname,
                    domain
                ],
                billingItem[
                    id,
                    nextInvoiceTotalRecurringAmount,
                    children[
                        categoryCode,
                        nextInvoiceTotalRecurringAmount
                    ],
                    orderItem[
                        id,
                        order.userRecord[
                            username
                        ]
                    ]
                ],
                datacenter[
                    id,
                    name,
                    longName
                ],
                guests[
                    id,
                    hostname,
                    domain,
                    uuid
                ],
                guestCount
            ''')

        return self.host.getObject(id=host_id, **kwargs)

    def place_order(self, hostname, domain, location, flavor, hourly, router=None):
        """Places an order for a dedicated host.

        See get_create_options() for valid arguments.

        :param string hostname: server hostname
        :param string domain: server domain name
        :param string location: location (datacenter) name
        :param boolean hourly: True if using hourly pricing (default).
                               False for monthly.
        :param int router: an optional value for selecting a backend router
        """
        create_options = self._generate_create_dict(hostname=hostname,
                                                    router=router,
                                                    domain=domain,
                                                    flavor=flavor,
                                                    datacenter=location,
                                                    hourly=hourly)

        return self.client['Product_Order'].placeOrder(create_options)

    def verify_order(self, hostname, domain, location, hourly, flavor, router=None):
        """Verifies an order for a dedicated host.

        See :func:`place_order` for a list of available options.
        """

        create_options = self._generate_create_dict(hostname=hostname,
                                                    router=router,
                                                    domain=domain,
                                                    flavor=flavor,
                                                    datacenter=location,
                                                    hourly=hourly)

        return self.client['Product_Order'].verifyOrder(create_options)

    def _generate_create_dict(self,
                              hostname=None,
                              domain=None,
                              flavor=None,
                              router=None,
                              datacenter=None,
                              hourly=True):
        """Translates args into a dictionary for creating a dedicated host."""
        package = self._get_package()
        item = self._get_item(package, flavor)

        location = self._get_location(package['regions'], datacenter)
        price = self._get_price(item)

        routers = self._get_backend_router(
            location['location']['locationPackageDetails'], item)

        router = self._get_default_router(routers, router)

        hardware = {
            'hostname': hostname,
            'domain': domain,
            'primaryBackendNetworkComponent': {
                'router': {
                    'id': router
                }
            }
        }

        complex_type = "SoftLayer_Container_Product_Order_Virtual_DedicatedHost"

        order = {
            "complexType": complex_type,
            "quantity": 1,
            'location': location['keyname'],
            'packageId': package['id'],
            'prices': [{'id': price}],
            'hardware': [hardware],
            'useHourlyPricing': hourly,
        }
        return order

    def _get_package(self):
        """Get the package related to simple dedicated host ordering."""
        mask = '''
        items[
            id,
            description,
            prices,
            capacity,
            keyName,
            itemCategory[categoryCode],
            bundleItems[capacity, categories[categoryCode]]
        ],
        regions[location[location[priceGroups]]]
        '''

        package_keyname = 'DEDICATED_HOST'
        package = self.ordering_manager.get_package_by_key(package_keyname, mask=mask)

        return package

    def _get_location(self, regions, datacenter):
        """Get the longer key with a short location(datacenter) name."""
        for region in regions:
            # list of locations
            if region['location']['location']['name'] == datacenter:
                return region

        raise SoftLayer.SoftLayerError("Could not find valid location for: '%s'" % datacenter)

    def get_create_options(self):
        """Returns valid options for ordering a dedicated host."""
        package = self._get_package()
        # Locations
        locations = []
        for region in package['regions']:
            locations.append({
                'name': region['location']['location']['longName'],
                'key': region['location']['location']['name'],
            })
        # flavors
        dedicated_host = []
        for item in package['items']:
            if item['itemCategory']['categoryCode'] == \
                    'dedicated_virtual_hosts':
                dedicated_host.append({
                    'name': item['description'],
                    'key': item['keyName'],
                })

        return {'locations': locations, 'dedicated_host': dedicated_host}

    def _get_price(self, package):
        """Returns valid price for ordering a dedicated host."""

        for price in package['prices']:
            if not price.get('locationGroupId'):
                return price['id']

        raise SoftLayer.SoftLayerError("Could not find valid price")

    def _get_item(self, package, flavor):
        """Returns the item for ordering a dedicated host."""

        for item in package['items']:
            if item['keyName'] == flavor:
                return item

        raise SoftLayer.SoftLayerError("Could not find valid item for: '%s'" % flavor)

    def _get_backend_router(self, locations, item):
        """Returns valid router options for ordering a dedicated host."""
        mask = '''
            id,
            hostname
        '''
        cpu_count = item['capacity']

        for capacity in item['bundleItems']:
            for category in capacity['categories']:
                if category['categoryCode'] == 'dedicated_host_ram':
                    mem_capacity = capacity['capacity']
                if category['categoryCode'] == 'dedicated_host_disk':
                    disk_capacity = capacity['capacity']

        if locations is not None:
            for location in locations:
                if location['locationId'] is not None:
                    loc_id = location['locationId']
                    host = {
                        'cpuCount': cpu_count,
                        'memoryCapacity': mem_capacity,
                        'diskCapacity': disk_capacity,
                        'datacenter': {
                            'id': loc_id
                        }
                    }
                    routers = self.host.getAvailableRouters(host, mask=mask)
                    return routers

        raise SoftLayer.SoftLayerError("Could not find available routers")

    def _get_default_router(self, routers, router_name=None):
        """Returns the default router for ordering a dedicated host."""
        if router_name is None:
            for router in routers:
                if router['id'] is not None:
                    return router['id']
        else:
            for router in routers:
                if router['hostname'] == router_name:
                    return router['id']

        raise SoftLayer.SoftLayerError("Could not find valid default router")

    def get_router_options(self, datacenter=None, flavor=None):
        """Returns available backend routers for the dedicated host."""
        package = self._get_package()

        location = self._get_location(package['regions'], datacenter)
        item = self._get_item(package, flavor)

        return self._get_backend_router(location['location']['locationPackageDetails'], item)
