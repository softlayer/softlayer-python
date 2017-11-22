"""
    SoftLayer.dedicatedhost
    ~~~~~~~~~~~~
    DH Manager/helpers

    :license: MIT, see License for more details.
"""

import logging
import SoftLayer

from SoftLayer.managers import ordering
from SoftLayer import utils

LOGGER = logging.getLogger(__name__)


class DedicatedHostManager(utils.IdentifierMixin, object):
    """Manages SoftLayer Dedicated Hosts.

        See product information here https://www.ibm.com/cloud/dedicated

        Example::
            # Initialize the DedicatedHostManager.
            # env variables. These can also be specified in ~/.softlayer,
            # or passed directly to SoftLayer.Client()
            # SL_USERNAME = YOUR_USERNAME
            # SL_API_KEY = YOUR_API_KEY
            import SoftLayer
            client = SoftLayer.Client()
            mgr = SoftLayer.DedicatedHostManager(client)

    :param SoftLayer.API.BaseClient client: the client instance
    :param SoftLayer.managers.OrderingManager ordering_manager: an optional
                                              manager to handle ordering.
                                              If none is provided, one will be
                                              auto initialized.
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

        Example::

        :param list tags: filter based on list of tags
        :param integer cpus: filter based on number of CPUS
        :param integer memory: filter based on amount of memory
        :param string hostname: filter based on hostname
        :param string disk: filter based on disk
        :param string datacenter: filter based on datacenter
        :param dict \\*\\*kwargs: response-level options (mask, limit, etc.)
        :returns: Returns a list of dictionaries representing the matching
                  dedicated host.



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

        call = 'getDedicatedHosts'

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
        func = getattr(self.account, call)
        return func(**kwargs)

    def get_host(self, host_id, **kwargs):
        """Get details about a dedicated host.

        :param integer : the host ID
        :returns: A dictionary containing a large amount of information about
                  the specified instance.

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
            kwargs['mask'] = (
                'id,'
                'name,'
                'cpuCount,'
                'memoryCapacity,'
                'diskCapacity,'
                'createDate,'
                'modifyDate,'
                'backendRouter[id, hostname, domain],'
                'billingItem[id, nextInvoiceTotalRecurringAmount, '
                'children[categoryCode,nextInvoiceTotalRecurringAmount],'
                'orderItem[id, order.userRecord[username]]],'
                'datacenter[id, name, longName],'
                'guests[id, hostname, domain, uuid],'
                'guestCount'
            )

        return self.host.getObject(id=host_id, **kwargs)

    def place_order(self, hostname, domain, location, hourly, router=None):
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
                                                    datacenter=location,
                                                    hourly=hourly)

        return self.client['Product_Order'].placeOrder(create_options)

    def verify_order(self, hostname, domain, location, hourly, router=None):
        """Verifies an order for a dedicated host.

        See :func:`place_order` for a list of available options.
        """

        create_options = self._generate_create_dict(hostname=hostname,
                                                    router=router,
                                                    domain=domain,
                                                    datacenter=location,
                                                    hourly=hourly)

        return self.client['Product_Order'].verifyOrder(create_options)

    def _generate_create_dict(self,
                              hostname=None,
                              router=None,
                              domain=None,
                              datacenter=None,
                              hourly=True):
        """Translates args into a dictionary for creating a dedicated host."""
        package = self._get_package()
        item = self._get_item(package)
        location = self._get_location(package['regions'], datacenter)
        price = self._get_price(item)

        if router is None:
            routers = self._get_backend_router(
                location['location']['locationPackageDetails'])
            router = self._get_default_router(routers)

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
            itemCategory[categoryCode]
        ],
        regions[location[location[priceGroups]]]
        '''

        package_keyname = 'DEDICATED_HOST'

        package = self.ordering_manager.get_package_by_key(package_keyname,
                                                           mask=mask)

        if package is None:
            raise SoftLayer.SoftLayerError("Ordering package not found")

        return package

    def _get_location(self, regions, datacenter):
        """Get the longer key with a short location(datacenter) name."""
        for region in regions:
            # list of locations
            if region['location']['location']['name'] == datacenter:
                return region

        raise SoftLayer.SoftLayerError("Could not find valid location for: '%s'"
                                       % datacenter)

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
        dedicated_host = []
        for item in package['items']:
            if item['itemCategory']['categoryCode'] == \
                    'dedicated_virtual_hosts':
                dedicated_host.append({
                    'name': item['description'],
                    'key': item['id'],
                })

        return {
            'locations': locations,
            'dedicated_host': dedicated_host,
        }

    def _get_price(self, package):
        """Returns valid price for ordering a dedicated host."""

        for price in package['prices']:
            if price.get('locationGroupId') is '':
                return price['id']

        raise SoftLayer.SoftLayerError(
            "Could not find valid price")

    def _get_item(self, package):
        """Returns the item for ordering a dedicated host."""
        description = '56 Cores X 242 RAM X 1.2 TB'

        for item in package['items']:
            if item['description'] == description:
                return item

        raise SoftLayer.SoftLayerError("Could not find valid item for: '%s'"
                                       % description)

    def _get_backend_router(self, locations):
        """Returns valid router options for ordering a dedicated host."""
        mask = '''
            id,
            hostname
        '''

        if locations is not None:
            for location in locations:
                if location['locationId'] is not None:
                    loc_id = location['locationId']
                    host = {
                        'cpuCount': 56,
                        'memoryCapacity': 242,
                        'diskCapacity': 1200,
                        'datacenter': {
                            'id': loc_id
                        }
                    }
                    routers = self.host.getAvailableRouters(host, mask=mask)
                    return routers

        raise SoftLayer.SoftLayerError("Could not find available routers")

    def _get_default_router(self, routers):
        """Returns the default router for ordering a dedicated host."""
        for router in routers:
            if router['id'] is not None:
                return router['id']

        raise SoftLayer.SoftLayerError("Could not find valid default router")
