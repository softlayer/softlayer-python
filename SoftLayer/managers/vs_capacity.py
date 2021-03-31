"""
    SoftLayer.vs_capacity
    ~~~~~~~~~~~~~~~~~~~~~~~
    Reserved Capacity Manager and helpers

    :license: MIT, see License for more details.
"""

import logging

from SoftLayer.exceptions import SoftLayerError
from SoftLayer.managers import ordering
from SoftLayer.managers.vs import VSManager
from SoftLayer import utils

# Invalid names are ignored due to long method names and short argument names
# pylint: disable=invalid-name, no-self-use

LOGGER = logging.getLogger(__name__)


class CapacityManager(utils.IdentifierMixin, object):
    """Manages SoftLayer Reserved Capacity Groups.

        Product Information

        - https://cloud.ibm.com/docs/virtual-servers?topic=virtual-servers-about-reserved-virtual-servers
        - https://softlayer.github.io/reference/services/SoftLayer_Virtual_ReservedCapacityGroup/
        - https://softlayer.github.io/reference/services/SoftLayer_Virtual_ReservedCapacityGroup_Instance/


    :param SoftLayer.API.BaseClient client: the client instance
    :param SoftLayer.managers.OrderingManager ordering_manager: an optional manager to handle ordering.
                                              If none is provided, one will be auto initialized.
    """

    def __init__(self, client, ordering_manager=None):
        self.client = client
        self.account = client['Account']
        self.capacity_package = 'RESERVED_CAPACITY'
        self.rcg_service = 'Virtual_ReservedCapacityGroup'

        if ordering_manager is None:
            self.ordering_manager = ordering.OrderingManager(client)

    def list(self):
        """List Reserved Capacities"""
        mask = """mask[availableInstanceCount, occupiedInstanceCount,
instances[id, billingItem[description, hourlyRecurringFee]], instanceCount, backendRouter[datacenter]]"""
        results = self.client.call('Account', 'getReservedCapacityGroups', mask=mask)
        return results

    def get_object(self, identifier, mask=None):
        """Get a Reserved Capacity Group

        :param int identifier: Id of the SoftLayer_Virtual_ReservedCapacityGroup
        :param string mask: override default object Mask
        """
        if mask is None:
            mask = "mask[instances[billingItem[item[keyName],category], guest], backendRouter[datacenter]]"
        result = self.client.call(self.rcg_service, 'getObject', id=identifier, mask=mask)
        return result

    def get_create_options(self):
        """List available reserved capacity plans"""
        mask = "mask[attributes,prices[pricingLocationGroup]]"
        results = self.ordering_manager.list_items(self.capacity_package, mask=mask)
        return results

    def get_available_routers(self, dc=None):
        """Pulls down all backendRouterIds that are available

        :param string dc: A specific location to get routers for, like 'dal13'.
        :returns list: A list of locations where RESERVED_CAPACITY can be ordered.
        """
        mask = "mask[locations]"
        # Step 1, get the package id
        package = self.ordering_manager.get_package_by_key(self.capacity_package, mask="id")

        # Step 2, get the regions this package is orderable in
        regions = self.client.call('Product_Package', 'getRegions', id=package['id'], mask=mask, iter=True)
        _filter = None
        routers = {}
        if dc is not None:
            _filter = {'datacenterName': {'operation': dc}}

        # Step 3, for each location in each region, get the pod details, which contains the router id
        pods = self.client.call('Network_Pod', 'getAllObjects', filter=_filter, iter=True)
        for region in regions:
            routers[region['keyname']] = []
            for location in region['locations']:
                location['location']['pods'] = list()
                for pod in pods:
                    if pod['datacenterName'] == location['location']['name']:
                        location['location']['pods'].append(pod)

        # Step 4, return the data.
        return regions

    def create(self, name, backend_router_id, flavor, instances, test=False):
        """Orders a Virtual_ReservedCapacityGroup

        :param string name: Name for the new reserved capacity
        :param int backend_router_id: This selects the pod. See create_options for a list
        :param string flavor: Capacity KeyName, see create_options for a list
        :param int instances: Number of guest this capacity can support
        :param bool test: If True, don't actually order, just test.
        """

        # Since orderManger needs a DC id, just send in 0, the API will ignore it
        args = (self.capacity_package, 0, [flavor])
        extras = {"backendRouterId": backend_router_id, "name": name}
        kwargs = {
            'extras': extras,
            'quantity': instances,
            'complex_type': 'SoftLayer_Container_Product_Order_Virtual_ReservedCapacity',
            'hourly': True
        }
        if test:
            receipt = self.ordering_manager.verify_order(*args, **kwargs)
        else:
            receipt = self.ordering_manager.place_order(*args, **kwargs)
        return receipt

    def create_guest(self, capacity_id, test, guest_object):
        """Turns an empty Reserve Capacity into a real Virtual Guest

        :param int capacity_id: ID of the RESERVED_CAPACITY_GROUP to create this guest into
        :param bool test: True will use verifyOrder, False will use placeOrder
        :param dictionary guest_object:  Below is the minimum info you need to send in
            guest_object = {
            'domain': 'test.com',
            'hostname': 'A1538172419',
            'os_code': 'UBUNTU_LATEST_64',
            'primary_disk': '25',
            }

        """

        vs_manager = VSManager(self.client)
        mask = "mask[instances[id, billingItem[id, item[id,keyName]]], backendRouter[id, datacenter[name]]]"
        capacity = self.get_object(capacity_id, mask=mask)
        try:
            capacity_flavor = capacity['instances'][0]['billingItem']['item']['keyName']
            flavor = _flavor_string(capacity_flavor, guest_object['primary_disk'])
        except KeyError as ex:
            raise SoftLayerError("Unable to find capacity Flavor.") from ex

        guest_object['flavor'] = flavor
        guest_object['datacenter'] = capacity['backendRouter']['datacenter']['name']

        # Reserved capacity only supports SAN as of 20181008
        guest_object['local_disk'] = False
        # Reserved capacity only supports monthly ordering via Virtual_Guest::generateOrderTemplate
        # Hourly ordering would require building out the order manually.
        guest_object['hourly'] = False
        template = vs_manager.verify_create_instance(**guest_object)
        template['reservedCapacityId'] = capacity_id
        if guest_object.get('ipv6'):
            ipv6_price = self.ordering_manager.get_price_id_list('PUBLIC_CLOUD_SERVER', ['1_IPV6_ADDRESS'])
            template['prices'].append({'id': ipv6_price[0]})

        if test:
            result = self.client.call('Product_Order', 'verifyOrder', template)
        else:
            result = self.client.call('Product_Order', 'placeOrder', template)

        return result


def _flavor_string(capacity_key, primary_disk):
    """Removed the _X_YEAR_TERM from capacity_key and adds the primary disk size, creating the flavor keyName

    This will work fine unless 10 year terms are invented... or flavor format changes...
    """
    flavor = "%sX%s" % (capacity_key[:-12], primary_disk)
    return flavor
