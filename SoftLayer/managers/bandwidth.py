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
