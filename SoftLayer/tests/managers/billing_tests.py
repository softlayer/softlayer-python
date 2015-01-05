"""
    SoftLayer.tests.managers.ticket_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import datetime
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

    def test_billing_summary_with_date(self):
        results = self.billing.list_resources(from_date='2014-02-06')
        test_date = datetime.date(2014, 2, 6)
        now = datetime.date.today()
        now_delta = now - datetime.date(2014, 2, 6)
        for result in results:
            create_date = result['createDate']
            row_date = datetime.datetime.strptime(create_date[0:10], '%Y-%m-%d')
            row_delta = now - row_date.date()
            self.assertTrue(now_delta >= row_delta)
