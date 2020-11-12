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

    def get_registration_detail_object(self, identifier, mask=None):
        """Calls SoftLayer_Account_Regional_Registry_Detail::getObject()

        :param identifier int: Account_Regional_Registry_Detail id
        :return dict: Account_Regional_Registry_Detail
        """
        if mask is None:
            mask = "mask[properties[propertyType]]"

        return self.client.call('Account_Regional_Registry_Detail', 'getObject', id=identifier, mask=mask)

    def edit_properties(self, properties):
        """Calls SoftLayer_Account_Regional_Registry_Detail_Property::editObjects(properties)

        :param properties list: SoftLayer_Account_Regional_Registry_Detail_Property. Needs id and value.
        :return bool: True on success, exception otherwise.
        """

        return self.client.call('Account_Regional_Registry_Detail_Property', 'editObjects', properties)

    def create_properties(self, properties):
        """Calls SoftLayer_Account_Regional_Registry_Detail_Property::createObjects(properties)

        :param properties list: SoftLayer_Account_Regional_Registry_Detail_Property. 
                                Needs propertyType->keyName and value.
        :return list: SoftLayer_Account_Regional_Registry_Detail_Property[]
        """

        return self.client.call('Account_Regional_Registry_Detail_Property', 'createObjects', properties)