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
        self.registration = self.client['Network_Subnet_Registration']

    def detail(self, identifier):
        """Gets subnet registration information

        :return: subnet registration object

        """

        mask = 'account,personDetail,networkDetail'
        return self.registration.getObject(mask=mask, id=identifier)
