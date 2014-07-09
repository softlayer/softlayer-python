"""
    SoftLayer.tests.CLI.modules.rwhois_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer.CLI.modules import rwhois
from SoftLayer import testing


class RWhoisTests(testing.TestCase):
    def set_up(self):
        self.client = testing.FixtureClient()

    def test_edit_nothing(self):
        command = rwhois.RWhoisEdit(client=self.client)
        self.assertRaises(exceptions.CLIAbort, command.execute, {})

    def test_edit(self):
        command = rwhois.RWhoisEdit(client=self.client)
        output = command.execute({'--abuse': 'abuse@site.com',
                                  '--address1': 'address line 1',
                                  '--address2': 'address line 2',
                                  '--company': 'Company, Inc',
                                  '--city': 'Dallas',
                                  '--country': 'United States',
                                  '--firstname': 'John',
                                  '--lastname': 'Smith',
                                  '--postal': '12345',
                                  '--state': 'TX',
                                  '--state': 'TX',
                                  '--private': True,
                                  '--public': False})

        self.assertEqual(None, output)
        service = self.client['Network_Subnet_Rwhois_Data']
        service.editObject.assert_called_with({'city': 'Dallas',
                                               'firstName': 'John',
                                               'companyName': 'Company, Inc',
                                               'address1': 'address line 1',
                                               'address2': 'address line 2',
                                               'lastName': 'Smith',
                                               'abuseEmail': 'abuse@site.com',
                                               'state': 'TX',
                                               'country': 'United States',
                                               'postalCode': '12345',
                                               'privateResidenceFlag': False},
                                              id='id')

    def test_edit_public(self):
        command = rwhois.RWhoisEdit(client=self.client)
        output = command.execute({'--private': False,
                                  '--public': True})

        self.assertEqual(None, output)
        service = self.client['Network_Subnet_Rwhois_Data']
        service.editObject.assert_called_with({'privateResidenceFlag': True},
                                              id='id')

    def test_show(self):
        command = rwhois.RWhoisShow(client=self.client)

        output = command.execute({})
        expected = {'Abuse Email': 'abuseEmail',
                    'Address 1': 'address1',
                    'Address 2': 'address2',
                    'City': 'city',
                    'Company': 'companyName',
                    'Country': 'country',
                    'Name': 'firstName lastName',
                    'Postal Code': 'postalCode',
                    'State': '-'}
        self.assertEqual(expected, formatting.format_output(output, 'python'))
