"""
    SoftLayer.tests.managers.registration_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.

    A lot of these tests will use junk data because the manager just passes
    them directly to the API.
"""
from SoftLayer import testing
from SoftLayer.managers.registration import RegistrationManager


class RegistrationTests(testing.TestCase):

    def set_up(self):
        self.registration_mgr = RegistrationManager(self.client)

    def test_detail(self):
        result = self.registration_mgr.detail(1536487)
        self.assertEqual(result['id'], 1536487)
        self.assert_called_with('SoftLayer_Network_Subnet', 'getActiveRegistration', identifier=1536487)

    def test_get_registration_detail_object(self):
        result = self.registration_mgr.get_registration_detail_object(51990)
        self.assertEqual(result['id'], 51990)
        self.assert_called_with('SoftLayer_Account_Regional_Registry_Detail', 'getObject', identifier=51990)

    def test_get_registration_detail_object_mask(self):
        result = self.registration_mgr.get_registration_detail_object(51990, mask="mask[id]")
        self.assertEqual(result['id'], 51990)
        self.assert_called_with('SoftLayer_Account_Regional_Registry_Detail', 'getObject',
                                identifier=51990, mask="mask[id]")

    def test_edit_properties(self):
        to_edit = [{"id": 12345, "value": "TEST"}]
        result = self.registration_mgr.edit_properties(to_edit)
        self.assertTrue(result)
        self.assert_called_with('SoftLayer_Account_Regional_Registry_Detail_Property', 'editObjects', args=(to_edit,))

    def test_create_properties(self):
        to_edit = [{"id": 12345, "value": "TEST"}]
        result = self.registration_mgr.create_properties(to_edit)
        self.assertTrue(result)
        self.assert_called_with('SoftLayer_Account_Regional_Registry_Detail_Property', 'createObjects', args=(to_edit,))

    def test_get_detail(self):
        identifier = 12345
        self.registration_mgr.detail(identifier)
        self.assert_called_with('SoftLayer_Network_Subnet',
                                'getActiveRegistration', identifier=identifier)

    def test_get_contact_properties(self):
        identifier = 12345
        mask = 'mask[propertyType]'
        result = self.registration_mgr.get_contact_properties(identifier)
        self.assertIsInstance(result, list)
        self.assert_called_with('SoftLayer_Account_Regional_Registry_Detail', 'getProperties',
                                identifier=identifier, mask=mask)

    def test_get_registration_details(self):
        identifier = 12345
        mask = 'mask[registration[status]]'
        object_filter = {'details': {'registration': {'status': {'keyName': {'operation': 'REGISTRATION_COMPLETE'}}}}}
        result = self.registration_mgr.get_registration_details(identifier)
        self.assertIsInstance(result, list)
        self.assert_called_with('SoftLayer_Account_Regional_Registry_Detail', 'getDetails',
                                filter=object_filter, identifier=identifier, mask=mask)

    def test_create_person_record(self):
        template_object = {
            'detailTypeId': 3,
            'properties': [
                {
                    "propertyTypeId": 3,
                    "value": "TestGuy",
                    "registrationDetailId": '12345',
                    'sequencePosition': 0
                }
            ]
        }

        result = self.registration_mgr.create_person_record(template_object)
        self.assertTrue(result)
        self.assert_called_with('SoftLayer_Account_Regional_Registry_Detail', 'createObject', args=(template_object,))

    def test_subnet_clear(self):
        identifier = 1234
        result = self.registration_mgr.clear(identifier)
        self.assertEqual(result, True)
        self.assert_called_with('SoftLayer_Network_Subnet_Registration',
                                'clearRegistration')
