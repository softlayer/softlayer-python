"""
    SoftLayer.dedicatedhost
    ~~~~~~~~~~~~~~~~~~~~~~~
    DH Manager/helpers

    :license: MIT, see License for more details.
"""
import logging

from SoftLayer.exceptions import SoftLayerAPIError
from SoftLayer.exceptions import SoftLayerError
from SoftLayer.managers import ordering
from SoftLayer import utils

# Invalid names are ignored due to long method names and short argument names
# pylint: disable=invalid-name

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
        self.guest = client['Virtual_Guest']

        if ordering_manager is None:
            self.ordering_manager = ordering.OrderingManager(client)

    def cancel_host(self, host_id):
        """Cancel a dedicated host immediately, it fails if there are still guests in the host.

        :param host_id: The ID of the dedicated host to be cancelled.
        :return: True on success or an exception

        Example::
            # Cancels dedicated host id 12345
            result = mgr.cancel_host(12345)

        """
        return self.host.deleteObject(id=host_id)

    def cancel_guests(self, host_id):
        """Cancel all guests into the dedicated host immediately.

        To cancel an specified guest use the method VSManager.cancel_instance()

        :param host_id: The ID of the dedicated host.
        :return: The id, fqdn and status of all guests into a dictionary. The status
                 could be 'Cancelled' or an exception message, The dictionary is empty
                 if there isn't any guest in the dedicated host.

        Example::
            # Cancel guests of dedicated host id 12345
            result = mgr.cancel_guests(12345)
        """
        result = []

        guests = self.host.getGuests(id=host_id, mask='id,fullyQualifiedDomainName')

        if guests:
            for vs in guests:
                status_info = {
                    'id': vs['id'],
                    'fqdn': vs['fullyQualifiedDomainName'],
                    'status': self._delete_guest(vs['id'])
                }
                result.append(status_info)

        return result

    def list_guests(self, host_id, tags=None, cpus=None, memory=None, hostname=None,
                    domain=None, local_disk=None, nic_speed=None, public_ip=None,
                    private_ip=None, **kwargs):
        """Retrieve a list of all virtual servers on the dedicated host.

        Example::

            # Print out a list of instances with 4 cpu cores in the host id 12345.

            for vsi in mgr.list_guests(host_id=12345, cpus=4):
               print vsi['fullyQualifiedDomainName'], vsi['primaryIpAddress']

            # Using a custom object-mask. Will get ONLY what is specified
            object_mask = "mask[hostname,monitoringRobot[robotStatus]]"
            for vsi in mgr.list_guests(mask=object_mask,cpus=4):
                print vsi

        :param integer host_id: the identifier of dedicated host
        :param list tags: filter based on list of tags
        :param integer cpus: filter based on number of CPUS
        :param integer memory: filter based on amount of memory
        :param string hostname: filter based on hostname
        :param string domain: filter based on domain
        :param string local_disk: filter based on local_disk
        :param integer nic_speed: filter based on network speed (in MBPS)
        :param string public_ip: filter based on public ip address
        :param string private_ip: filter based on private ip address
        :param dict \\*\\*kwargs: response-level options (mask, limit, etc.)
        :returns: Returns a list of dictionaries representing the matching
                  virtual servers
        """
        if 'mask' not in kwargs:
            items = [
                'id',
                'globalIdentifier',
                'hostname',
                'domain',
                'fullyQualifiedDomainName',
                'primaryBackendIpAddress',
                'primaryIpAddress',
                'lastKnownPowerState.name',
                'hourlyBillingFlag',
                'powerState',
                'maxCpu',
                'maxMemory',
                'datacenter',
                'activeTransaction.transactionStatus[friendlyName,name]',
                'status',
            ]
            kwargs['mask'] = "mask[%s]" % ','.join(items)

        _filter = utils.NestedDict(kwargs.get('filter') or {})

        if tags:
            _filter['guests']['tagReferences']['tag']['name'] = {
                'operation': 'in',
                'options': [{'name': 'data', 'value': tags}],
            }

        if cpus:
            _filter['guests']['maxCpu'] = utils.query_filter(cpus)

        if memory:
            _filter['guests']['maxMemory'] = utils.query_filter(memory)

        if hostname:
            _filter['guests']['hostname'] = utils.query_filter(hostname)

        if domain:
            _filter['guests']['domain'] = utils.query_filter(domain)

        if local_disk is not None:
            _filter['guests']['localDiskFlag'] = (
                utils.query_filter(bool(local_disk)))

        if nic_speed:
            _filter['guests']['networkComponents']['maxSpeed'] = (
                utils.query_filter(nic_speed))

        if public_ip:
            _filter['guests']['primaryIpAddress'] = (
                utils.query_filter(public_ip))

        if private_ip:
            _filter['guests']['primaryBackendIpAddress'] = (
                utils.query_filter(private_ip))

        kwargs['filter'] = _filter.to_dict()
        kwargs['iter'] = True
        return self.host.getGuests(id=host_id, **kwargs)

    def list_instances(self, tags=None, hostname=None,
                       datacenter=None, order=None, owner=None):
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
        _filter = utils.NestedDict({})
        if tags:
            _filter['dedicatedHosts']['tagReferences']['tag']['name'] = {
                'operation': 'in',
                'options': [{'name': 'data', 'value': tags}],
            }

        if hostname:
            _filter['dedicatedHosts']['name'] = (
                utils.query_filter(hostname)
            )

        if datacenter:
            _filter['dedicatedHosts']['datacenter']['name'] = (
                utils.query_filter(datacenter))

        if order:
            _filter['dedicatedHosts']['billingItem']['orderItem']['order']['id'] = (
                utils.query_filter(order))

        if owner:
            _filter['dedicatedHosts']['billingItem']['orderItem']['order']['userRecord']['username'] = (
                utils.query_filter(owner))

        object_filter = _filter.to_dict()
        object_mask = "mask[id,name,createDate,cpuCount,diskCapacity,memoryCapacity,guestCount," \
                      "datacenter,backendRouter,allocationStatus,billingItem[orderItem[order[userRecord]]]]"
        return self.account.getDedicatedHosts(mask=object_mask, filter=object_filter)

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
            kwargs['mask'] = '''
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
            '''

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
            bundleItems[capacity,keyName,categories[categoryCode],hardwareGenericComponentModel[id,
            hardwareComponentType[keyName]]]
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

        raise SoftLayerError("Could not find valid location for: '%s'" % datacenter)

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

        raise SoftLayerError("Could not find valid price")

    def _get_item(self, package, flavor):
        """Returns the item for ordering a dedicated host."""

        for item in package['items']:
            if item['keyName'] == flavor:
                return item

        raise SoftLayerError("Could not find valid item for: '%s'" % flavor)

    def _get_backend_router(self, locations, item):
        """Returns valid router options for ordering a dedicated host."""
        mask = '''
            id,
            hostname
        '''
        cpu_count = item['capacity']
        mem_capacity = {}
        disk_capacity = {}
        gpuComponents = {}
        for capacity in item['bundleItems']:
            for category in capacity['categories']:
                if category['categoryCode'] == 'dedicated_host_ram':
                    mem_capacity = capacity['capacity']
                if category['categoryCode'] == 'dedicated_host_disk':
                    disk_capacity = capacity['capacity']

        for hardwareComponent in item['bundleItems']:
            if hardwareComponent['keyName'].find("GPU") != -1:
                hardwareComponentType = hardwareComponent['hardwareGenericComponentModel']['hardwareComponentType']
                gpuComponents = [
                    {
                        'hardwareComponentModel': {
                            'hardwareGenericComponentModel': {
                                'id': hardwareComponent['hardwareGenericComponentModel']['id'],
                                'hardwareComponentType': {
                                    'keyName': hardwareComponentType['keyName']
                                }
                            }
                        }
                    },
                    {
                        'hardwareComponentModel': {
                            'hardwareGenericComponentModel': {
                                'id': hardwareComponent['hardwareGenericComponentModel']['id'],
                                'hardwareComponentType': {
                                    'keyName': hardwareComponentType['keyName']
                                }
                            }
                        }
                    }
                ]

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
                    if item['keyName'].find("GPU") != -1:
                        host['pciDevices'] = gpuComponents
                    routers = self.host.getAvailableRouters(host, mask=mask)
                    return routers

        raise SoftLayerError("Could not find available routers")

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

        raise SoftLayerError("Could not find valid default router")

    def get_router_options(self, datacenter=None, flavor=None):
        """Returns available backend routers for the dedicated host."""
        package = self._get_package()

        location = self._get_location(package['regions'], datacenter)
        item = self._get_item(package, flavor)

        return self._get_backend_router(location['location']['locationPackageDetails'], item)

    def _delete_guest(self, guest_id):
        """Deletes a guest and returns 'Cancelled' or and Exception message"""
        msg = 'Cancelled'
        try:
            self.guest.deleteObject(id=guest_id)
        except SoftLayerAPIError as e:
            msg = 'Exception: ' + e.faultString

        return msg
