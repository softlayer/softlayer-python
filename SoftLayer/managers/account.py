"""
    SoftLayer.account
    ~~~~~~~~~~~~~~~~~~~~~~~
    Account manager

    :license: MIT, see License for more details.
"""

import logging
import SoftLayer

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
        return self.client.call('Notification_Occurrence_Event', 'acknowledgeNotification', id=event_id)

    def get_event(self, event_id):
        mask = """mask[
            acknowledgedFlag,
            attachments,
            impactedResources,
            statusCode,
            updates,
            notificationOccurrenceEventType]
        """
        return self.client.call('Notification_Occurrence_Event', 'getObject', id=event_id, mask=mask)

    def get_invoices(self, limit, closed=False, get_all=False):
        mask = "mask[invoiceTotalAmount, itemCount]"
        _filter = {
            'invoices': {
                'createDate' : {
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

    def get_child_items(self, identifier):
        mask = "mask[id, description, oneTimeAfterTaxAmount, recurringAfterTaxAmount, category[name], location[name]]"
        return self.client.call('Billing_Invoice_Item', 'getChildren', id=identifier, mask=mask)
