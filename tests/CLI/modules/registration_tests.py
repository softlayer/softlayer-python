import json

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
        self.assert_called_with('SoftLayer_Account', 'getSubnets')

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
