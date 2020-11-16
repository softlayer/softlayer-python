"""
    SoftLayer.subnet_registration
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Regional Internet Registry (RIR) Manager

    :license: MIT, see License for more details.
"""


class RegistrationManager(object):
    """Manage SoftLayer Subnet registrations with Regional Internet Registry (RIR)c

    :param SoftLayer.API.BaseClient client: the client instance

    """

    def __init__(self, client):
        self.client = client
        self.account = client['Account']
        self.registration = self.client['Network_Subnet_Registration']

    def detail(self, identifier):
        """Gets subnet registration information

        :return: subnet registration object

        """

        mask = 'account,personDetail,networkDetail'
        return self.registration.getObject(mask=mask, id=identifier)

    def get_registration_details(self, mask=None):
        """Returns the RWhois information about the current account.

        :returns: A dictionary containing the account's RWhois information.
        """
        if mask is None:
            mask = 'detailType,properties[id,propertyType[keyName,id],value]'

        filter_object = {'subnetRegistrationDetails': {'detailTypeId': {'operation': 3}}}

        return self.account.getSubnetRegistrationDetails(mask=mask, filter=filter_object)
