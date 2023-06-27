"""
    SoftLayer.bandwidth
    ~~~~~~~~~~~~~~~~~~~~~~~
    Bandwidth manager

    :license: MIT, see License for more details.
"""

from SoftLayer import utils

# pylint: disable=invalid-name


class BandwidthManager(utils.IdentifierMixin, object):
    """Common functions for getting information from the Bandwidth service

    :param SoftLayer.API.BaseClient client: the client instance
    """

    def __init__(self, client):
        self.client = client

    def get_location_group(self):
        """Gets some basic bandwidth information

        :return: Bandwidth object
        """
        _filters = {"locationGroupTypeId": {"operation": 1}}

        return self.client.call('Location_Group', 'getAllObjects', filter=_filters)

    def create_pool(self, name_pool, id_location_group):
        """Gets some basic bandwidth information

        :return: Bandwidth object
        """
        current_user = self.client.call('Account', 'getCurrentUser')
        template = {
            "accountId": current_user['accountId'],
            "bandwidthAllotmentTypeId": 2,
            "locationGroupId": id_location_group,
            "name": name_pool
        }

        return self.client.call('Network_Bandwidth_Version1_Allotment', 'createObject', template)

    def get_bandwidth_detail(self, identifier):
        """Gets bandwidth pool detail.

        :returns: bandwidth pool detail
        """
        _mask = """activeDetails[allocation],projectedPublicBandwidthUsage, billingCyclePublicBandwidthUsage,
        hardware[outboundBandwidthUsage,bandwidthAllotmentDetail[allocation]],inboundPublicBandwidthUsage,
        virtualGuests[outboundPublicBandwidthUsage,bandwidthAllotmentDetail[allocation]],
        bareMetalInstances[outboundBandwidthUsage,bandwidthAllotmentDetail[allocation]]"""
        return self.client['SoftLayer_Network_Bandwidth_Version1_Allotment'].getObject(id=identifier, mask=_mask)

    def edit_pool(self, identifier, new_name_pool):
        """Edit bandwidth pool name

        :return: Bandwidth object
        """
        actual_bandwidth = self.get_bandwidth_detail(identifier)
        template = {
            "accountId": actual_bandwidth.get('accountId'),
            "bandwidthAllotmentTypeId": actual_bandwidth.get('bandwidthAllotmentTypeId'),
            "locationGroupId": actual_bandwidth.get('locationGroupId'),
            "name": new_name_pool
        }

        return self.client.call('Network_Bandwidth_Version1_Allotment', 'editObject', template, id=identifier)

    def delete_pool(self, identifier):
        """Delete bandwidth pool

        :return: Boolean value
        """
        return self.client.call('Network_Bandwidth_Version1_Allotment', 'requestVdrCancellation', id=identifier)
