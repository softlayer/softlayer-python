"""
    SoftLayer.tests.managers.ticket_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import SoftLayer
from SoftLayer import testing


class BillingTests(testing.TestCase):

    def set_up(self):
        self.billing = SoftLayer.BillingManager(self.client)

    def test_list_billing_items(self):
        self.billing.list_resources()
        self.assert_called_with('SoftLayer_Account', 'getOrders')

    def test_billing_info(self):
        self.billing.get_info()
        self.assert_called_with('SoftLayer_Account', 'getBillingInfo')

    def test_billing_summary(self):
        self.billing.get_summary()
        self.assert_called_with('SoftLayer_Account',
                                'getNextInvoiceTotalAmount')
        self.assert_called_with('SoftLayer_Account', 'getLatestBillDate')
        self.assert_called_with('SoftLayer_Account', 'getBalance')
