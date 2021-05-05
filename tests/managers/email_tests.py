"""
    SoftLayer.tests.managers.email_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

from SoftLayer.managers.email import EmailManager
from SoftLayer import testing


class AccountManagerTests(testing.TestCase):

    def test_get_AccountOverview(self):
        self.manager = EmailManager(self.client)
        self.manager.get_AccountOverview(1232123)
        self.assert_called_with('SoftLayer_Network_Message_Delivery_Email_Sendgrid',
                                'getAccountOverview')

    def test_get_statistics(self):
        self.manager = EmailManager(self.client)
        self.manager.get_statistics(1232123,
                                    ["requests", "delivered", "opens", "clicks", "bounds"],
                                    True,
                                    True, True, 6)
        self.assert_called_with('SoftLayer_Network_Message_Delivery_Email_Sendgrid',
                                'getStatistics')
