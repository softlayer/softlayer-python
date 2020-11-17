"""
    SoftLayer.tests.managers.registration_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.

    A lot of these tests will use junk data because the manager just passes
    them directly to the API.
"""
from SoftLayer.managers.registration import RegistrationManager
from SoftLayer import testing


class RegistrationTests(testing.TestCase):

    def set_up(self):
        self.registration_mgr = RegistrationManager(self.client)

    def test_get_detail(self):
        identifier = 12345
        self.registration_mgr.detail(identifier)
        self.assert_called_with('SoftLayer_Network_Subnet_Registration',
                                'getObject',
                                identifier=identifier)

    def test_get_contact_properties(self):
        identifier = 12345
        mask = 'mask[propertyType]'
        result = self.registration_mgr.get_contact_properties(identifier)
        self.assertIsInstance(result, list)
        self.assert_called_with('SoftLayer_Account_Regional_Registry_Detail',
                                'getProperties',
                                identifier=identifier,
                                mask=mask)

    def test_get_registration_details(self):
        identifier = 12345
        mask = 'mask[registration[status]]'
        object_filter = {'details': {'registration': {'status': {'keyName': {'operation': 'REGISTRATION_COMPLETE'}}}}}
        result = self.registration_mgr.get_registration_details(identifier)
        self.assertIsInstance(result, list)
        self.assert_called_with('SoftLayer_Account_Regional_Registry_Detail',
                                'getDetails',
                                filter=object_filter,
                                identifier=identifier,
                                mask=mask)
