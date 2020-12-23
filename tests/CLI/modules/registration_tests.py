import json

import mock

from SoftLayer import exceptions
from SoftLayer import testing


class RegistrationTests(testing.TestCase):

    def test_detail(self):
        result = self.run_command(['registration', 'subnet-detail', '1536487'])
        self.assert_no_fail(result)
        result_output = json.loads(result.output)
        self.assertEqual(result_output['id'], 1536487)
        self.assertEqual(result_output['Name'], 'test Example')

    def test_show(self):
        result = self.run_command(['registration', 'show'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Account', 'getPublicSubnets')

    def test_show_username(self):
        result = self.run_command(['registration', 'show', '--username', 'test'])
        self.assert_no_fail(result)
        self.assertTrue(result.output, [])

    def test_show_status(self):
        result = self.run_command(['registration', 'show', '--status', 'Complete'])
        self.assert_no_fail(result)
        self.assertTrue(result.output, [])

    def test_person_edit_basic(self):
        result = self.run_command(['registration', 'person-edit', '12345', '--first_name', 'TestGuy'])
        expected_edit = [{"id": 85644, "value": "TestGuy", "propertyType": {"keyName": "FIRST_NAME"}}]
        self.assert_no_fail(result)
        self.assertIn("Successfully edited properties.", result.output)
        self.assert_called_with('SoftLayer_Account_Regional_Registry_Detail', 'getObject', identifier='12345')
        self.assert_called_with('SoftLayer_Account_Regional_Registry_Detail_Property', 'editObjects',
                                args=(expected_edit,))

    def test_person_edit_new(self):
        result = self.run_command(['registration', 'person-edit', '12345', '--last_name', 'TestGuy'])
        expected_edit = [
            {
                "propertyTypeId": 3,  # From PROPERTY_TYPES in SoftLayer/CLI/registration/person_edit.py
                "value": "TestGuy",
                "registrationDetailId": '12345',
                'sequencePosition': 0
            }
        ]
        self.assert_no_fail(result)
        self.assertIn("Successfully created properties.", result.output)
        self.assert_called_with('SoftLayer_Account_Regional_Registry_Detail', 'getObject', identifier='12345')
        self.assert_called_with('SoftLayer_Account_Regional_Registry_Detail_Property', 'createObjects',
                                args=(expected_edit,))

    def test_person_edit_new_failure(self):
        edit_mock = self.set_mock('SoftLayer_Account_Regional_Registry_Detail_Property', 'createObjects')
        edit_mock.side_effect = exceptions.SoftLayerAPIError("SoftLayer_Exception_Public", "Testing Failure")
        result = self.run_command(['registration', 'person-edit', '12345', '--last_name', 'TestGuy'])
        expected_edit = [
            {
                "propertyTypeId": 3,  # From PROPERTY_TYPES in SoftLayer/CLI/registration/person_edit.py
                "value": "TestGuy",
                "registrationDetailId": '12345',
                'sequencePosition': 0
            }
        ]

        self.assertIsNotNone(result.exception)
        self.assertIn("Testing Failure", result.exception.faultString)
        self.assert_called_with('SoftLayer_Account_Regional_Registry_Detail', 'getObject', identifier='12345')
        self.assert_called_with('SoftLayer_Account_Regional_Registry_Detail_Property', 'createObjects',
                                args=(expected_edit,))

    def test_person_edit_edit_failure(self):
        edit_mock = self.set_mock('SoftLayer_Account_Regional_Registry_Detail_Property', 'editObjects')
        edit_mock.side_effect = exceptions.SoftLayerAPIError("SoftLayer_Exception_Public", "Testing Failure")
        result = self.run_command(['registration', 'person-edit', '12345', '--first_name', 'TestGuy'])
        expected_edit = [{"id": 85644, "value": "TestGuy", "propertyType": {"keyName": "FIRST_NAME"}}]

        self.assertIsNotNone(result.exception)
        self.assertIn("Testing Failure", result.exception.faultString)
        self.assert_called_with('SoftLayer_Account_Regional_Registry_Detail', 'getObject', identifier='12345')
        self.assert_called_with('SoftLayer_Account_Regional_Registry_Detail_Property', 'editObjects',
                                args=(expected_edit,))

    def test_contacts(self):
        result = self.run_command(['registration', 'contacts'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Account', 'getSubnetRegistrationDetails')

    def test_person_detail(self):
        result = self.run_command(['registration', 'person-detail', '1234'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Account_Regional_Registry_Detail', 'getProperties')
        self.assert_called_with('SoftLayer_Account_Regional_Registry_Detail', 'getDetails')

    def test_subnet_register(self):
        result = self.run_command(['registration', 'subnet-register', '12345', '9999'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Network_Subnet_Registration', 'createObject')
        self.assert_called_with('SoftLayer_Network_Subnet', 'getObject', identifier='12345')

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_person_create(self, confirm_mock):
        confirm_mock.return_value = True
        result = self.run_command(['registration', 'person-create', '--organization', 'Organization Test',
                                   '--first_name', 'TestName', '--last_name', 'TestLastName',
                                   '--address', '1234 Alpha Rd', '--city', 'Dallas', '--country', 'US',
                                   '--state', 'Texas', '--postal_code', '4521-4123', '--email_address', 'test@ibm.com',
                                   '--abuse_email', 'test2@ibm.com', '--phone', '2717874571'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Account_Regional_Registry_Detail', 'createObject', args=mock.ANY)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_person_create_no_confirm(self, confirm_mock):
        confirm_mock.return_value = False
        result = self.run_command(['registration', 'person-create', '--organization', 'Organization Test',
                                   '--first_name', 'TestName', '--last_name', 'TestLastName',
                                   '--address', '1234 Alpha Rd', '--city', 'Dallas', '--country', 'US',
                                   '--state', 'Texas', '--postal_code', '4521-4123', '--email_address', 'test@ibm.com',
                                   '--abuse_email', 'test2@ibm.com', '--phone', '2717874571'])
        self.assertEqual(result.exit_code, 2)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_person_create_with_no_confirm(self, confirm_mock):
        confirm_mock.return_value = False
        result = self.run_command(['registration', 'person-create', '--organization', 'Organization Test',
                                   '--first_name', 'TestName', '--last_name', 'TestLastName',
                                   '--address', '1234 Alpha Rd', '--city', 'Dallas', '--country', 'US',
                                   '--state', 'Texas', '--postal_code', '4521-4123', '--email_address', 'test@ibm.com',
                                   '--abuse_email', 'test2@ibm.com', '--phone', '2717874571'])
        self.assertIn("Canceling creation!", result.exception.message)
        self.assertEqual(result.exit_code, 2)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_subnet_clear_True(self, confirm_mock):
        confirm_mock.return_value = True
        result = self.run_command(['--really', 'registration', 'subnet-clear', '1234'])
        self.assert_no_fail(result)
        self.assertEqual('The subnet registration with id 1234 was successfully cleared\n', result.output)
        self.assert_called_with('SoftLayer_Network_Subnet_Registration', 'clearRegistration', args=mock.ANY)

    @mock.patch('SoftLayer.RegistrationManager.clear')
    def test_subnet_clear_False(self, clear_mock):
        clear_mock.return_value = False
        result = self.run_command(['--really', 'registration', 'subnet-clear', '1234'])
        self.assert_no_fail(result)
        self.assertEqual('Unable to clear the subnet registration with id 1234\n', result.output)

    @mock.patch('SoftLayer.RegistrationManager.clear')
    def test_subnet_clear_no_registration(self, clear_mock):
        clear_mock.return_value = None
        result = self.run_command(['--really', 'registration', 'subnet-clear', '1234'])
        self.assertIn("Could not clear the subnet", result.exception.message)
        self.assertEqual(result.exit_code, 2)
