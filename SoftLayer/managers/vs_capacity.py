"""
    SoftLayer.vs_capacity
    ~~~~~~~~~~~~~~~~~~~~~~~
    Reserved Capacity Manager and helpers

    :license: MIT, see License for more details.
"""

import logging
import SoftLayer

from SoftLayer.managers import ordering
from SoftLayer import utils

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

        if ordering_manager is None:
            self.ordering_manager = ordering.OrderingManager(client)

    def list(self):
        results = self.client.call('Account', 'getReservedCapacityGroups')
        return results

    def get_create_options(self):
        mask = "mask[attributes,prices[pricingLocationGroup]]"
        # mask = "mask[id, description, capacity, units]"
        results = self.ordering_manager.list_items(self.capacity_package, mask=mask)
        return results