"""
    SoftLayer.tests.managers.email_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

from SoftLayer.managers.email import EmailManager
from SoftLayer import testing


class EmailManagerTests(testing.TestCase):

    def test_get_AccountOverview(self):
        self.manager = EmailManager(self.client)
        self.manager.get_account_overview(1232123)
        self.assert_called_with('SoftLayer_Network_Message_Delivery_Email_Sendgrid',
                                'getAccountOverview')

    def test_get_statistics(self):
        self.manager = EmailManager(self.client)
        self.manager.get_statistics(1232123, 6)
        self.assert_called_with('SoftLayer_Network_Message_Delivery_Email_Sendgrid',
                                'getStatistics')

    def test_get_object(self):
        self.manager = EmailManager(self.client)
        self.manager.get_instance(1232123)
        self.assert_called_with('SoftLayer_Network_Message_Delivery_Email_Sendgrid',
                                'getObject')

    def test_update_email_address(self):
        self.manager = EmailManager(self.client)
        self.manager.update_email(1232123, 'test@ibm.com')
        self.assert_called_with('SoftLayer_Network_Message_Delivery_Email_Sendgrid',
                                'updateEmailAddress')
