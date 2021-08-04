"""
    SoftLayer.tests.managers.account_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

from SoftLayer.managers.account import AccountManager as AccountManager
from SoftLayer import SoftLayerAPIError
from SoftLayer import testing


class AccountManagerTests(testing.TestCase):

    def set_up(self):
        self.manager = AccountManager(self.client)
        self.SLNOE = 'SoftLayer_Notification_Occurrence_Event'

    def test_get_summary(self):
        self.manager.get_summary()
        self.assert_called_with('SoftLayer_Account', 'getObject')

    def test_get_planned_upcoming_events(self):
        self.manager.get_upcoming_events("PLANNED")
        self.assert_called_with(self.SLNOE, 'getAllObjects')

    def test_get_unplanned_upcoming_events(self):
        self.manager.get_upcoming_events("UNPLANNED_INCIDENT")
        self.assert_called_with(self.SLNOE, 'getAllObjects')

    def test_get_announcement_upcoming_events(self):
        self.manager.get_upcoming_events("ANNOUNCEMENT")
        self.assert_called_with(self.SLNOE, 'getAllObjects')

    def test_add_planned_event_filter(self):
        event_type = 'PLANNED'
        _filter = {
            'notificationOccurrenceEventType': {
                'keyName': {
                    'operation': event_type
                }
            }
        }
        self.manager.add_event_filter(_filter, event_type)

    def test_add_unplanned_event_filter(self):
        event_type = 'UNPLANNED_INCIDENT'
        _filter = {
            'notificationOccurrenceEventType': {
                'keyName': {
                    'operation': event_type
                }
            }
        }
        self.manager.add_event_filter(_filter, event_type)

    def test_add_announcement_event_filter(self):
        event_type = 'ANNOUNCEMENT'
        _filter = {
            'notificationOccurrenceEventType': {
                'keyName': {
                    'operation': event_type
                }
            }
        }
        self.manager.add_event_filter(_filter, event_type)

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

    def test_get_billing_item_from_invoice(self):
        self.manager.get_billing_item_from_invoice(12345)
        self.assert_called_with('SoftLayer_Billing_Invoice_Item', 'getBillingItem', identifier=12345)

    def test_get_item_details_with_billing_item_id(self):
        self.manager.get_item_detail(12345)
        self.assert_called_with('SoftLayer_Billing_Item', 'getObject', identifier=12345)

    def test_get_item_details_with_invoice_item_id(self):
        mock = self.set_mock('SoftLayer_Billing_Item', 'getObject')
        mock.side_effect = SoftLayerAPIError(404, "Unable to find object with id of '123456'.")
        self.manager.get_item_detail(123456)
        self.assert_called_with('SoftLayer_Billing_Item', 'getObject', identifier=123456)
        self.assert_called_with('SoftLayer_Billing_Invoice_Item', 'getBillingItem', identifier=123456)

    def test_get_routers(self):
        self.manager.get_routers()
        self.assert_called_with("SoftLayer_Account", "getRouters")

    def test_get_active_account_licenses(self):
        self.manager.get_active_account_licenses()
        self.assert_called_with("SoftLayer_Account", "getActiveAccountLicenses")

    def test_get_active_virtual_licenses(self):
        self.manager.get_active_virtual_licenses()
        self.assert_called_with("SoftLayer_Account", "getActiveVirtualLicenses")

    def test_get_routers_with_datacenter(self):
        self.manager.get_routers(location='dal13')
        object_filter = {'routers': {'topLevelLocation': {'name': {'operation': 'dal13'}}}}
        self.assert_called_with("SoftLayer_Account", "getRouters", filter=object_filter)
