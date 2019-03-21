"""
    SoftLayer.account
    ~~~~~~~~~~~~~~~~~~~~~~~
    Account manager

    :license: MIT, see License for more details.
"""

import logging

from SoftLayer import utils

# Invalid names are ignored due to long method names and short argument names
# pylint: disable=invalid-name, no-self-use

LOGGER = logging.getLogger(__name__)


class AccountManager(utils.IdentifierMixin, object):
    """Common functions for getting information from the Account service

    :param SoftLayer.API.BaseClient client: the client instance
    """

    def __init__(self, client):
        self.client = client

    def get_summary(self):
        """Gets some basic account information

        :return: Account object
        """
        mask = """mask[
            nextInvoiceTotalAmount,
            pendingInvoice[invoiceTotalAmount],
            blockDeviceTemplateGroupCount,
            dedicatedHostCount,
            domainCount,
            hardwareCount,
            networkStorageCount,
            openTicketCount,
            networkVlanCount,
            subnetCount,
            userCount,
            virtualGuestCount
            ]
        """
        return self.client.call('Account', 'getObject', mask=mask)

    def get_upcoming_events(self):
        """Retreives a list of Notification_Occurrence_Events that have not ended yet

        :return: SoftLayer_Notification_Occurrence_Event
        """
        mask = "mask[id, subject, startDate, endDate, statusCode, acknowledgedFlag, impactedResourceCount, updateCount]"
        _filter = {
            'endDate': {
                'operation': '> sysdate'
            },
            'startDate': {
                'operation': 'orderBy',
                'options': [{
                    'name': 'sort',
                    'value': ['ASC']
                }]
            }
        }
        return self.client.call('Notification_Occurrence_Event', 'getAllObjects', filter=_filter, mask=mask, iter=True)

    def ack_event(self, event_id):
        """Acknowledge an event. This mostly prevents it from appearing as a notification in the control portal.

        :param int event_id: Notification_Occurrence_Event ID you want to ack
        :return: True on success, Exception otherwise.
        """
        return self.client.call('Notification_Occurrence_Event', 'acknowledgeNotification', id=event_id)

    def get_event(self, event_id):
        """Gets details about a maintenance event

        :param int event_id: Notification_Occurrence_Event ID
        :return: Notification_Occurrence_Event
        """
        mask = """mask[
            acknowledgedFlag,
            attachments,
            impactedResources,
            statusCode,
            updates,
            notificationOccurrenceEventType]
        """
        return self.client.call('Notification_Occurrence_Event', 'getObject', id=event_id, mask=mask)

    def get_invoices(self, limit=50, closed=False, get_all=False):
        """Gets an accounts invoices.

        :param int limit: Number of invoices to get back in a single call.
        :param bool closed: If True, will also get CLOSED invoices
        :param bool get_all: If True, will paginate through invoices until all have been retrieved.
        :return: Billing_Invoice
        """
        mask = "mask[invoiceTotalAmount, itemCount]"
        _filter = {
            'invoices': {
                'createDate': {
                    'operation': 'orderBy',
                    'options': [{
                        'name': 'sort',
                        'value': ['DESC']
                    }]
                },
                'statusCode': {'operation': 'OPEN'},
            }
        }
        if closed:
            del _filter['invoices']['statusCode']

        return self.client.call('Account', 'getInvoices', mask=mask, filter=_filter, iter=get_all, limit=limit)

    def get_billing_items(self, identifier):
        """Gets all topLevelBillingItems from a specific invoice

        :param int identifier: Invoice Id
        :return: Billing_Invoice_Item
        """

        mask = """mask[
            id, description, hostName, domainName, oneTimeAfterTaxAmount, recurringAfterTaxAmount, createDate,
            categoryCode,
            category[name],
            location[name],
            children[id, category[name], description, oneTimeAfterTaxAmount, recurringAfterTaxAmount]
        ]"""
        return self.client.call(
            'Billing_Invoice',
            'getInvoiceTopLevelItems',
            id=identifier,
            mask=mask,
            iter=True,
            limit=100
        )
