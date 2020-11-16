"""
    SoftLayer.managers.registration
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Regional Internet Registry (RIR) Manager

    :license: MIT, see License for more details.
"""


class RegistrationManager(object):
    """Manage SoftLayer Subnet registrations with Regional Internet Registry (RIR)

    :param SoftLayer.API.BaseClient client: the client instance

    """

    def __init__(self, client):
        self.client = client
        self.account = client['Account']
        self.registration = self.client['Network_Subnet_Registration']
        self.PERSON = 3 # a person has a detailTypeId == 3
        self.regional_register = self.client['Account_Regional_Registry_Detail']

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

    def get_registration_details(self, mask=None):
        """Returns the Contact Person information about the current account.

        :returns: A dictionary containing the account's RWhois information.
        """

        if mask is None:
            mask = 'detailType,properties[id,propertyType[keyName,id],value]'

        filter_object = {'subnetRegistrationDetails': {'detailTypeId': {'operation': self.PERSON}}}

        return self.account.getSubnetRegistrationDetails(mask=mask, filter=filter_object)

    def get_contact_properties(self, identifier):
        """Gets contact properties information.

        :return: A list of contact properties information.

        """
        mask = 'mask[propertyType]'
        return self.regional_register.getProperties(mask=mask, id=identifier, iter=True)

    def get_registration_details(self, identifier):
        """Gets registration details.

        :return: A list of registration details.

        """
        mask = "mask[registration[status]]"
        object_filter = {"details": {"registration": {"status": {"keyName": {"operation": "REGISTRATION_COMPLETE"}}}}}

        return self.regional_register.getDetails(mask=mask, filter=object_filter, id=identifier, iter=True)

