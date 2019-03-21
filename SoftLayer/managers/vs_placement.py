"""
    SoftLayer.vs_placement
    ~~~~~~~~~~~~~~~~~~~~~~~
    Placement Group Manager

    :license: MIT, see License for more details.
"""

import logging

from SoftLayer import utils

# Invalid names are ignored due to long method names and short argument names
# pylint: disable=invalid-name, no-self-use

LOGGER = logging.getLogger(__name__)


class PlacementManager(utils.IdentifierMixin, object):
    """Manages SoftLayer Reserved Capacity Groups.

        Product Information

        - https://console.test.cloud.ibm.com/docs/vsi/vsi_placegroup.html#placement-groups
        - https://softlayer.github.io/reference/services/SoftLayer_Account/getPlacementGroups/
        - https://softlayer.github.io/reference/services/SoftLayer_Virtual_PlacementGroup_Rule/

        Existing instances cannot be added to a placement group.
        You can only add a virtual server instance to a placement group at provisioning.
        To remove an instance from a placement group, you must delete or reclaim the instance.

    :param SoftLayer.API.BaseClient client: the client instance
    """

    def __init__(self, client):
        self.client = client
        self.account = client['Account']
        self.resolvers = [self._get_id_from_name]

    def list(self, mask=None):
        """List existing placement groups

        Calls SoftLayer_Account::getPlacementGroups
         """
        if mask is None:
            mask = "mask[id, name, createDate, rule, guestCount, backendRouter[id, hostname]]"
        groups = self.client.call('Account', 'getPlacementGroups', mask=mask, iter=True)
        return groups

    def create(self, placement_object):
        """Creates a placement group

        A placement_object is defined as::

            placement_object = {
                'backendRouterId': 12345,
                'name': 'Test Name',
                'ruleId': 12345
            }

        -  https://softlayer.github.io/reference/datatypes/SoftLayer_Virtual_PlacementGroup/

        :param dictionary placement_object:

        """
        return self.client.call('SoftLayer_Virtual_PlacementGroup', 'createObject', placement_object)

    def get_routers(self):
        """Calls SoftLayer_Virtual_PlacementGroup::getAvailableRouters()"""
        return self.client.call('SoftLayer_Virtual_PlacementGroup', 'getAvailableRouters')

    def get_object(self, group_id, mask=None):
        """Returns a PlacementGroup Object

        https://softlayer.github.io/reference/services/SoftLayer_Virtual_PlacementGroup/getObject
        """
        if mask is None:
            mask = "mask[id, name, createDate, rule, backendRouter[id, hostname]," \
                   "guests[activeTransaction[id,transactionStatus[name,friendlyName]]]]"
        return self.client.call('SoftLayer_Virtual_PlacementGroup', 'getObject', id=group_id, mask=mask)

    def delete(self, group_id):
        """Deletes a PlacementGroup

        Placement group must be empty to be deleted.
        https://softlayer.github.io/reference/services/SoftLayer_Virtual_PlacementGroup/deleteObject
        """
        return self.client.call('SoftLayer_Virtual_PlacementGroup', 'deleteObject', id=group_id)

    def get_all_rules(self):
        """Returns all available rules for creating a placement group"""
        return self.client.call('SoftLayer_Virtual_PlacementGroup_Rule', 'getAllObjects')

    def get_rule_id_from_name(self, name):
        """Finds the rule that matches name.

        SoftLayer_Virtual_PlacementGroup_Rule.getAllObjects doesn't support objectFilters.
        """
        results = self.client.call('SoftLayer_Virtual_PlacementGroup_Rule', 'getAllObjects')
        return [result['id'] for result in results if result['keyName'] == name.upper()]

    def get_backend_router_id_from_hostname(self, hostname):
        """Finds the backend router Id that matches the hostname given

        No way to use an objectFilter to find a backendRouter, so we have to search the hard way.
        """
        results = self.client.call('SoftLayer_Network_Pod', 'getAllObjects')
        return [result['backendRouterId'] for result in results if result['backendRouterName'] == hostname.lower()]

    def _get_id_from_name(self, name):
        """List placement group ids which match the given name."""
        _filter = {
            'placementGroups': {
                'name': {'operation': name}
            }
        }
        mask = "mask[id, name]"
        results = self.client.call('Account', 'getPlacementGroups', filter=_filter, mask=mask)
        return [result['id'] for result in results]
