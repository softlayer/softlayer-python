"""
    SoftLayer.tests.CLI.modules.email_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Tests for the user cli command
"""
from SoftLayer import testing


class EmailCLITests(testing.TestCase):

    def test_list(self):
        result = self.run_command(['email', 'list'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Account', 'getNetworkMessageDeliveryAccounts')

    def test_detail(self):
        result = self.run_command(['email', 'detail', '1232123'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Network_Message_Delivery_Email_Sendgrid', 'getObject')

    def test_edit(self):
        result = self.run_command(['email', 'edit', '1232123',
                                   '--username=test@ibm.com',
                                   '--email=test@ibm.com',
                                   '--password=test123456789'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Network_Message_Delivery_Email_Sendgrid',
                                'editObject')
        self.assert_called_with('SoftLayer_Network_Message_Delivery_Email_Sendgrid',
                                'updateEmailAddress')
