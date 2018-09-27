"""
    SoftLayer.vs_capacity
    ~~~~~~~~~~~~~~~~~~~~~~~
    Reserved Capacity Manager and helpers

    :license: MIT, see License for more details.
"""

import logging
import SoftLayer

from SoftLayer.managers import ordering
from SoftLayer.managers.vs import VSManager
from SoftLayer import utils

from pprint import pprint as pp
# Invalid names are ignored due to long method names and short argument names
# pylint: disable=invalid-name, no-self-use

LOGGER = logging.getLogger(__name__)

class CapacityManager(utils.IdentifierMixin, object):
    """Manages SoftLayer Dedicated Hosts.

        See product information here https://www.ibm.com/cloud/dedicated


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
        mask = """mask[availableInstanceCount, occupiedInstanceCount, 
instances[id, billingItem[description, hourlyRecurringFee]], instanceCount, backendRouter[datacenter]]"""
        results = self.client.call('Account', 'getReservedCapacityGroups', mask=mask)
        return results

    def get_object(self, identifier, mask=None):
        if mask is None:
            mask = "mask[instances[billingItem[item[keyName],category], guest], backendRouter[datacenter]]"
        result = self.client.call(self.rcg_service, 'getObject', id=identifier, mask=mask)
        return result

    def get_create_options(self):
        mask = "mask[attributes,prices[pricingLocationGroup]]"
        # mask = "mask[id, description, capacity, units]"
        results = self.ordering_manager.list_items(self.capacity_package, mask=mask)
        return results

    def get_available_routers(self):
        """Pulls down all backendRouterIds that are available"""
        mask = "mask[locations]"
        # Step 1, get the package id
        package = self.ordering_manager.get_package_by_key(self.capacity_package, mask="id")

        # Step 2, get the regions this package is orderable in
        regions = self.client.call('Product_Package', 'getRegions', id=package['id'], mask=mask)
        _filter = {'datacenterName': {'operation': ''}}
        routers = {}

        # Step 3, for each location in each region, get the pod details, which contains the router id
        for region  in regions:
            routers[region['keyname']] = []
            for location in region['locations']:
                location['location']['pods'] = list()
                _filter['datacenterName']['operation'] = location['location']['name']
                location['location']['pods'] = self.client.call('Network_Pod', 'getAllObjects', filter=_filter)

        # Step 4, return the data.
        return regions

    def create(self, name, datacenter, backend_router_id, capacity, quantity, test=False):
        """Orders a Virtual_ReservedCapacityGroup"""
        args = (self.capacity_package, datacenter, [capacity])
        extras = {"backendRouterId": backend_router_id, "name": name}
        kwargs = {
            'extras': extras,
            'quantity': quantity,
            'complex_type': 'SoftLayer_Container_Product_Order_Virtual_ReservedCapacity',
            'hourly': True
        }
        if test:
            receipt = self.ordering_manager.verify_order(*args, **kwargs)
        else:
            receipt = self.ordering_manager.place_order(*args, **kwargs)
        return receipt

    def create_guest(self, capacity_id, test, guest_object):
        vs_manager = VSManager(self.client)
        mask = "mask[instances[id, billingItem[id, item[id,keyName]]], backendRouter[id, datacenter[name]]]"
        capacity = self.get_object(capacity_id)
        try:
            capacity_flavor = capacity['instances'][0]['billingItem']['item']['keyName']
            flavor = _flavor_string(capacity_flavor, guest_object['primary_disk'])
        except KeyError:
            raise SoftLayer.SoftLayerError("Unable to find capacity Flavor.") 

        guest_object['flavor'] =  flavor
        guest_object['datacenter'] = capacity['backendRouter']['datacenter']['name']
        # pp(guest_object)
        
        template = vs_manager.verify_create_instance(**guest_object)
        template['reservedCapacityId'] = capacity_id
        if guest_object.get('ipv6'):
            ipv6_price = self.ordering_manager.get_price_id_list('PUBLIC_CLOUD_SERVER', ['1_IPV6_ADDRESS'])
            template['prices'].append({'id': ipv6_price[0]})
            
        # pp(template)
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

