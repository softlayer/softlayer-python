"""
    SoftLayer.tests.CLI.modules.account_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Tests for the user cli command
"""
import json
import sys

import mock
import testtools

from SoftLayer import testing


class AccountCLITests(testing.TestCase):

    def set_up(self):
        self.SLNOE = 'SoftLayer_Notification_Occurrence_Event'

    #### slcli account event-detail ####
    def test_event_detail(self):
        result = self.run_command(['account', 'event-detail', '1234'])
        self.assert_no_fail(result)
        self.assert_called_with(self.SLNOE, 'getObject', identifier='1234')

    def test_event_details_ack(self):
        result = self.run_command(['account', 'event-detail', '1234', '--ack'])
        self.assert_no_fail(result)
        self.assert_called_with(self.SLNOE, 'getObject', identifier='1234')
        self.assert_called_with(self.SLNOE, 'acknowledgeNotification', identifier='1234')

    #### slcli account events ####
    def test_events(self):
        result = self.run_command(['account', 'events'])
        self.assert_no_fail(result)
        self.assert_called_with(self.SLNOE, 'getAllObjects')

    def test_event_ack_all(self):
        result = self.run_command(['account', 'events', '--ack-all'])
        self.assert_called_with(self.SLNOE, 'getAllObjects')
        self.assert_called_with(self.SLNOE, 'acknowledgeNotification', identifier=1234)

    #### slcli account invoice-detail ####

    def test_invoice_detail(self):
        result = self.run_command(['account', 'invoice-detail', '1234'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Billing_Invoice', 'getInvoiceTopLevelItems', identifier='1234')

    def test_invoice_detail(self):
        result = self.run_command(['account', 'invoice-detail', '1234', '--details'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Billing_Invoice', 'getInvoiceTopLevelItems', identifier='1234')

    #### slcli account invoices ####
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

    #### slcli account summary ####
        result = self.run_command(['account', 'summary'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Account', 'getObject')
