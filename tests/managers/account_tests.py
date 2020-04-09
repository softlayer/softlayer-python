"""
    SoftLayer.tests.managers.account_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

from SoftLayer.managers.account import AccountManager as AccountManager
from SoftLayer import testing


class AccountManagerTests(testing.TestCase):

    def set_up(self):
        self.manager = AccountManager(self.client)
        self.SLNOE = 'SoftLayer_Notification_Occurrence_Event'

    def test_get_summary(self):
        self.manager.get_summary()
        self.assert_called_with('SoftLayer_Account', 'getObject')

    def test_get_upcoming_events(self):
        self.manager.get_upcoming_events()
        self.assert_called_with(self.SLNOE, 'getAllObjects')

    def test_ack_event(self):
        self.manager.ack_event(12345)
        self.assert_called_with(self.SLNOE, 'acknowledgeNotification', identifier=12345)

    def test_get_event(self):
        self.manager.get_event(12345)
        self.assert_called_with(self.SLNOE, 'getObject', identifier=12345)

    def test_get_invoices(self):
        self.manager.get_invoices()
        self.assert_called_with('SoftLayer_Account', 'getInvoices')

    def test_get_invoices_closed(self):
        self.manager.get_invoices(closed=True)
        _filter = {
            'invoices': {
                'createDate': {
                    'operation': 'orderBy',
                    'options': [{
                        'name': 'sort',
                        'value': ['DESC']
                    }]
                }
            }
        }
        self.assert_called_with('SoftLayer_Account', 'getInvoices', filter=_filter)

    def test_get_billing_items(self):
        self.manager.get_billing_items(12345)
        self.assert_called_with('SoftLayer_Billing_Invoice', 'getInvoiceTopLevelItems')

    def test_get_account_billing_items(self):
        self.manager.get_account_billing_items()
        object_filter = {
            "allTopLevelBillingItems": {
                "cancellationDate": {
                    "operation": "is null"
                },
                "createDate": {
                    'operation': 'orderBy',
                    'options': [{
                        'name': 'sort',
                        'value': ['ASC']
                    }]
                }
            }
        }

        self.assert_called_with('SoftLayer_Account', 'getAllTopLevelBillingItems',
                                offset=0, limit=100, filter=object_filter)
        self.manager.get_account_billing_items(mask="id")
        self.assert_called_with('SoftLayer_Account', 'getAllTopLevelBillingItems', mask="mask[id]")

    def test_get_billing_item(self):
        self.manager.get_billing_item(12345)
        self.assert_called_with('SoftLayer_Billing_Item', 'getObject', identifier=12345)
        self.manager.get_billing_item(12345, mask="id")
        self.assert_called_with('SoftLayer_Billing_Item', 'getObject', identifier=12345, mask="mask[id]")

    def test_cancel_item(self):
        self.manager.cancel_item(12345)
        reason = "No longer needed"
        note = "Cancelled by testAccount with the SLCLI"
        self.assert_called_with('SoftLayer_Billing_Item', 'cancelItem',
                                args=(False, True, reason, note), identifier=12345)
        reason = "TEST"
        note = "note test"
        self.manager.cancel_item(12345, reason, note)
        self.assert_called_with('SoftLayer_Billing_Item', 'cancelItem',
                                args=(False, True, reason, note), identifier=12345)
