"""
    SoftLayer.tests.CLI.modules.rwhois_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
from SoftLayer.CLI import exceptions
from SoftLayer import testing

import json


class RWhoisTests(testing.TestCase):
    def test_edit_nothing(self):

        result = self.run_command(['rwhois', 'edit'])

        self.assertEqual(result.exit_code, 2)
        self.assertIsInstance(result.exception, exceptions.CLIAbort)

    def test_edit(self):

        result = self.run_command(['rwhois', 'edit',
                                   '--abuse=abuse@site.com',
                                   '--address1=address line 1',
                                   '--address2=address line 2',
                                   '--company=Company, Inc',
                                   '--city=Dallas',
                                   '--country=United States',
                                   '--firstname=John',
                                   '--lastname=Smith',
                                   '--postal=12345',
                                   '--state=TX',
                                   '--state=TX',
                                   '--private'])

        self.assert_no_fail(result)
        self.assertEqual(result.output, "")

        self.assert_called_with('SoftLayer_Network_Subnet_Rwhois_Data',
                                'editObject',
                                args=({'city': 'Dallas',
                                       'firstName': 'John',
                                       'companyName': 'Company, Inc',
                                       'address1': 'address line 1',
                                       'address2': 'address line 2',
                                       'lastName': 'Smith',
                                       'abuseEmail': 'abuse@site.com',
                                       'state': 'TX',
                                       'country': 'United States',
                                       'postalCode': '12345',
                                       'privateResidenceFlag': True},),
                                identifier='id')

    def test_edit_public(self):
        result = self.run_command(['rwhois', 'edit', '--public'])

        self.assert_no_fail(result)
        self.assertEqual(result.output, "")

        self.assert_called_with('SoftLayer_Network_Subnet_Rwhois_Data',
                                'editObject',
                                args=({'privateResidenceFlag': False},),
                                identifier='id')

    def test_show(self):
        self.maxDiff = 100000
        result = self.run_command(['rwhois', 'show'])

        expected = {'Abuse Email': 'abuseEmail',
                    'Address 1': 'address1',
                    'Address 2': 'address2',
                    'City': 'city',
                    'Company': 'companyName',
                    'Country': 'country',
                    'Name': 'firstName lastName',
                    'Postal Code': 'postalCode',
                    'State': '-',
                    'Private Residence': True}
        self.assert_no_fail(result)
        self.assertEqual(json.loads(result.output), expected)
