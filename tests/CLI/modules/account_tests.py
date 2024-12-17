"""
    SoftLayer.tests.CLI.modules.account_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Tests for the user cli command
"""
import json

from SoftLayer.fixtures import SoftLayer_Account as SoftLayer_Account
from SoftLayer import testing


class AccountCLITests(testing.TestCase):

    def set_up(self):
        self.SLNOE = 'SoftLayer_Notification_Occurrence_Event'

    # slcli account event-detail
    def test_event_detail(self):
        result = self.run_command(['account', 'event-detail', '1234'])
        self.assert_no_fail(result)
        self.assert_called_with(self.SLNOE, 'getObject', identifier='1234')

    def test_event_details_ack(self):
        result = self.run_command(['account', 'event-detail', '1234', '--ack'])
        self.assert_no_fail(result)
        self.assert_called_with(self.SLNOE, 'getObject', identifier='1234')
        self.assert_called_with(self.SLNOE, 'acknowledgeNotification', identifier='1234')

    # slcli account events
    def test_events(self):
        result = self.run_command(['account', 'events'])
        self.assert_no_fail(result)
        self.assert_called_with(self.SLNOE, 'getAllObjects')

    def test_event_ack_all(self):
        result = self.run_command(['account', 'events', '--ack-all'])
        self.assert_no_fail(result)
        self.assert_called_with(self.SLNOE, 'getAllObjects')
        self.assert_called_with(self.SLNOE, 'acknowledgeNotification', identifier=1234)

    def test_event_jsonraw_output(self):
        # https://github.com/softlayer/softlayer-python/issues/1545
        command = '--format jsonraw account events'
        command_params = command.split()
        result = self.run_command(command_params)
        json_text_tables = result.stdout.split('\n')
        # removing an extra item due to an additional Newline at the end of the output
        json_text_tables.pop()
        # each item in the json_text_tables should be a list
        for json_text_table in json_text_tables:
            json_table = json.loads(json_text_table)
            self.assertIsInstance(json_table, list)

    # slcli account invoice-detail
    def test_invoice_detail(self):
        result = self.run_command(['account', 'invoice-detail', '1234'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Billing_Invoice', 'getInvoiceTopLevelItems', identifier='1234')

    def test_invoice_detail_details(self):
        result = self.run_command(['account', 'invoice-detail', '1234', '--details'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Billing_Invoice', 'getInvoiceTopLevelItems', identifier='1234')

    def test_invoice_detail_sum_children(self):
        result = self.run_command(['--format=json', 'account', 'invoice-detail', '1234', '--details'])
        self.assert_no_fail(result)
        json_out = json.loads(result.output)
        self.assertEqual(len(json_out), 7)
        self.assertEqual(json_out[0]['Item Id'], 724951323)
        self.assertEqual(json_out[0]['Single'], '$55.50')
        self.assertEqual(json_out[0]['Monthly'], '$0.10')
        self.assertEqual(json_out[3]['Item Id'], 1111222)
        self.assertEqual(json_out[3]['Single'], '$0.00')
        self.assertEqual(json_out[3]['Monthly'], '$30.36')

    def test_invoice_detail_csv_output_format(self):
        result = self.run_command(["--format", "csv", 'account', 'invoice-detail', '1234'])
        result_output = result.output.replace('\r', '').split('\n')
        self.assert_no_fail(result)
        self.assertEqual(result_output[0], '"Item Id","Category","Description","Single","Monthly",'
                         '"Create Date","Location"')
        self.assertEqual(result_output[1], '724951323,"Private (only) Secondary VLAN IP Addresses",'
                                           '"64 Portable Private IP Addresses (bleg.beh.com)",'
                                           '"$55.50","$0.10","2018-04-04","fra02"')

    # slcli account invoices
    def test_invoices(self):
        result = self.run_command(['account', 'invoices'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Account', 'getInvoices', limit=50)

    def test_invoices_limited(self):
        result = self.run_command(['account', 'invoices', '--limit=10'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Account', 'getInvoices', limit=10)

    def test_invoices_closed(self):
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
        result = self.run_command(['account', 'invoices', '--closed'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Account', 'getInvoices', limit=50, filter=_filter)

    def test_invoices_all(self):
        result = self.run_command(['account', 'invoices', '--all'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Account', 'getInvoices', limit=50)

    def test_single_invoice(self):
        amock = self.set_mock('SoftLayer_Account', 'getInvoices')
        amock.return_value = SoftLayer_Account.getInvoices[0]
        result = self.run_command(['account', 'invoices', '--limit=1'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Account', 'getInvoices', limit=1)

    # slcli account summary
    def test_account_summary(self):
        result = self.run_command(['account', 'summary'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Account', 'getObject')

    # slcli account billing-items
    def test_account_billing_items(self):
        result = self.run_command(['account', 'billing-items'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Account', 'getAllTopLevelBillingItems')

    def test_account_billing_items_by_category(self):
        result = self.run_command(['account', 'billing-items', '--category', 'server'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Account', 'getAllTopLevelBillingItems')

    def test_account_billing_items_by_ordered(self):
        result = self.run_command(['account', 'billing-items', '--ordered', 'Test'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Account', 'getAllTopLevelBillingItems')

    def test_account_billing_items_create(self):
        result = self.run_command(['account', 'billing-items', '--create', '04-21-2023'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Account', 'getAllTopLevelBillingItems')

    # slcli account item-detail
    def test_account_get_billing_item_detail(self):
        result = self.run_command(['account', 'item-detail', '12345'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Billing_Item', 'getObject', identifier='12345')

    # slcli account cancel-item
    def test_account_cancel_item(self):
        result = self.run_command(['account', 'cancel-item', '12345'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Billing_Item', 'cancelItem', identifier='12345')

    def test_acccount_order(self):
        result = self.run_command(['account', 'orders'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Billing_Order', 'getAllObjects')

    def test_acccount_licenses(self):
        result = self.run_command(['account', 'licenses'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Account', 'getActiveVirtualLicenses')
        self.assert_called_with('SoftLayer_Account', 'getActiveAccountLicenses')

    def test_acccount_provisioning_hook(self):
        result = self.run_command(['account', 'hooks'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Account', 'getPostProvisioningHooks')

    def test_created_provisioning_hook(self):
        result = self.run_command(['account', 'hook-create', '--name', 'testslcli', '--uri', 'http://slclitest.com'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Provisioning_Hook', 'createObject')

    def test_delete_provisioning_hook(self):
        result = self.run_command(['account', 'hook-delete', '123456'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Provisioning_Hook', 'deleteObject')

    def test_order_upgrade(self):
        result = self.run_command(['account', 'orders', '--upgrades'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Account', 'getUpgradeRequests')

    def test_account_events(self):
        result = self.run_command(['account', 'events', '--date-min', '5/9/2023'])
        self.assert_no_fail(result)
        self.assert_called_with(self.SLNOE, 'getAllObjects')

    def test_account_planned_events(self):
        result = self.run_command(['account', 'events', '--planned'])
        self.assert_no_fail(result)
        self.assert_called_with(self.SLNOE, 'getAllObjects')

    def test_account_unplanned_events(self):
        result = self.run_command(['account', 'events', '--unplanned'])
        self.assert_no_fail(result)
        self.assert_called_with(self.SLNOE, 'getAllObjects')

    def test_account_announcement_events(self):
        result = self.run_command(['account', 'events', '--announcement'])
        self.assert_no_fail(result)
        self.assert_called_with(self.SLNOE, 'getAllObjects')
