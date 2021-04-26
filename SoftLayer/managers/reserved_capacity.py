"""
    SoftLayer.reservedcapacity
    ~~~~~~~~~~~~~~~~
    Reserved Capacity Manager/helpers

    :license: MIT, see LICENSE for more details.
"""
from SoftLayer import utils


class ReservedCapacityManager(utils.IdentifierMixin, object):
    """Manages SoftLayer Reserved Capacity.

    :param SoftLayer.API.BaseClient client: the client instance

    """

    def __init__(self, client):
        self.client = client
        self.account = self.client['Account']
        self.rcg_service = 'Virtual_ReservedCapacityGroup'

    def detail(self, identifier, mask=None):
        """Get the Reserved Capacity detail.

        :param int identifier: Id of the SoftLayer_Virtual_ReservedCapacityGroup.
        :param string mask: Override default object Mask.
        """
        if mask is None:
            mask = "mask[id,name,createDate,modifyDate,backendRouter[id,hostname,datacenter]," \
                   "instances[id,guestId,guest[status,primaryBackendIpAddress,primaryIpAddress]," \
                   "availableFlag,billingItem[item[keyName,capacity,units]]],instanceCount," \
                   "availableInstanceCount,occupiedInstanceCount]"
        result = self.client.call(self.rcg_service, 'getObject', id=identifier, mask=mask)
        return result

    def vs_instances(self, identifier, mask=None):
        """List the Reserved Capacity Virtual Server Instances.

        :param int identifier: Id of the SoftLayer_Virtual_ReservedCapacityGroup
        :param string mask: Override default object Mask.
        """
        if mask is None:
            mask = "mask[guest[status,primaryBackendIpAddress,primaryIpAddress,datacenter]]"
        result = self.client.call(self.rcg_service, 'getInstances', id=identifier, mask=mask)
        return result

    def edit(self, identifier, name):
        """Edit a specific Reserved Capacity instance.

        :param int identifier: Id of the SoftLayer_Virtual_ReservedCapacityGroup
        :param string name: The new Reserved Capacity name to be edited.
        """
        template_object = {
            'id': identifier,
            'name': name
        }
        result = self.client.call(self.rcg_service, 'editObject', template_object, id=identifier)
        return result
