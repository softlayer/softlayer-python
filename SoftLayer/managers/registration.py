"""
    SoftLayer.managers.registration
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Regional Internet Registry (RIR) Manager

    :license: MIT, see License for more details.
"""
from SoftLayer import utils


class RegistrationManager(object):
    """Manage SoftLayer Subnet registrations with Regional Internet Registry (RIR)

    :param SoftLayer.API.BaseClient client: the client instance
    """

    def __init__(self, client):
        self.client = client
        self.account = client['Account']
        self.registration = self.client['Network_Subnet_Registration']
        self.person_type_id = 3  # a person has a detailTypeId == 3
        # 4 is a DETAULT_PERSON
        # 1 is NETWORK
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

    def get_account_contacts(self, mask=None):
        """Gets the Registry Details that pertain to the Person/Contact type.

        :returns list: SoftLayer_Account_Regional_Registry_Detail[]
        """

        if mask is None:
            mask = 'detailType,properties[id,propertyType[keyName,id],value]'

        filter_object = {'subnetRegistrationDetails': {'detailTypeId': {'operation': self.person_type_id}}}

        return self.client.call('Account', 'getSubnetRegistrationDetails', mask=mask, filter=filter_object)

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

    def register(self, subnet_id, contact_id):
        """Registers subnet to contact

        :param int subnet_id: Id of a Network_Subnet
        :param int contact_id: Id of a Account_Regional_Registry_Detail that is a person
        """
        subnet_mask = "mask[id,networkIdentifier,cidr,activeRegistration]"
        subnet = self.client.call('Network_Subnet', 'getObject', id=subnet_id, mask=subnet_mask)
        active_registration = subnet.get('activeRegistration')
        #  Active registration need to be edited.
        if active_registration:
            #  SoftLayer_Network_Subnet_Registration::editObject() just doesn't seem to work.
            #  This is how the portal edits a registration, so copying that workflow.
            registration_id = active_registration.get('id')
            details = self.client.call('SoftLayer_Network_Subnet_Registration', 'getDetailReferences',
                                       id=registration_id, mask="mask[detail[detailType]]")

            person_param = {
                'detailId': contact_id,
                'id': None,
                'registrationId': registration_id
            }
            network_param = {
                'detailId': None,
                'id': None,
                'registrationId': registration_id
            }
            for detail in details:
                if utils.lookup(detail, 'detail', 'detailType', 'keyName') == "NETWORK":
                    network_param['id'] = detail.get('id')
                    network_param['detailId'] = utils.lookup(detail, 'detail', 'id')
                else:
                    person_param['id'] = detail.get('id')
            return self.client.call('SoftLayer_Network_Subnet_Registration', 'editRegistrationAttachedDetails',
                                    person_param, network_param, id=registration_id)

        else:
            new_registration = {
                'networkIdentifier': subnet.get('networkIdentifier'),
                'cidr': subnet.get('cidr'),
                'detailReferences': [
                    {'detailId': contact_id}
                ],
            }
            return self.client.call('SoftLayer_Network_Subnet_Registration', 'createObject', new_registration)


class ContactPerson(object):
    """Turns a SoftLayer_Account_Regional_Registry_Detail into a useable datastructure

    Make sure to cast to a str() before putting this in a Table.
    `TypeError: 'NoneType' object is not iterable` Will result otherwise.
    """

    def __init__(self, registry_detail):
        """Sets up the person, populated with data from the SoftLayer API

        :param registry_detail: A SoftLayer_Account_Regional_Registry_Detail object.
        """
        self.properties = registry_detail.get('properties', [])
        self.id = registry_detail.get('id')  # pylint: disable=invalid-name
        for property_contact in self.properties:
            setattr(self, property_contact['propertyType']['keyName'], property_contact.get('value'))

    def __repr__(self):
        """Prints out First + Last name"""
        return "{} {}".format(self.FIRST_NAME, self.LAST_NAME)

    def __getattr__(self, attr):
        """To handle some cases where attributes don't exist nicely. Only called when objects do not exist.

        https://docs.python.org/3/reference/datamodel.html#object.__getattr__
        """
        return None

    def get(self, attr, default='None'):
        """To mimic the dictionaries .get() method"""
        value = getattr(self, attr)
        if value is None:
            return default
        return value
