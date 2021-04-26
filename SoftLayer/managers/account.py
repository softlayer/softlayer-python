"""
    SoftLayer.account
    ~~~~~~~~~~~~~~~~~~~~~~~
    Account manager

    :license: MIT, see License for more details.
"""

import logging

from SoftLayer import SoftLayerAPIError
from SoftLayer import utils

# Invalid names are ignored due to long method names and short argument names
# pylint: disable=invalid-name, no-self-use

LOGGER = logging.getLogger(__name__)


class AccountManager(utils.IdentifierMixin, object):
    """Common functions for getting information from the Account service

    :param SoftLayer.API.BaseClient client: the client instance
    """
    _DEFAULT_BILLING_ITEM_MASK = """mask[
                    orderItem[id,order[id,userRecord[id,email,displayName,userStatus]]],
                    nextInvoiceTotalRecurringAmount,
                    location, hourlyFlag, children
                ]"""

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

    def get_upcoming_events(self, event_type):
        """Retrieves a list of Notification_Occurrence_Events that have not ended yet

        :param: String event_type: notification event type.
        :return: SoftLayer_Notification_Occurrence_Event
        """
        mask = "mask[id, subject, startDate, endDate, modifyDate, statusCode, acknowledgedFlag, " \
               "impactedResourceCount, updateCount, systemTicketId, notificationOccurrenceEventType[keyName]]"

        _filter = {
            'notificationOccurrenceEventType': {
                'keyName': {
                    'operation': event_type
                }
            }
        }

        self.add_event_filter(_filter, event_type)

        return self.client.call('Notification_Occurrence_Event', 'getAllObjects', filter=_filter, mask=mask, iter=True)

    @staticmethod
    def add_event_filter(_filter, event_type):
        """Add data to the object filter.

        :param: _filter: event filter.
        :param: string event_type: event type.
        """
        if event_type == 'PLANNED':
            _filter['endDate'] = {
                'operation': '> sysdate - 2'
            }
            _filter['startDate'] = {
                'operation': 'orderBy',
                'options': [{
                    'name': 'sort',
                    'value': ['DESC']
                }]
            }

        if event_type == 'UNPLANNED_INCIDENT':
            _filter['modifyDate'] = {
                'operation': '> sysdate - 2'
            }

        if event_type == 'ANNOUNCEMENT':
            _filter['statusCode'] = {
                'keyName': {
                    'operation': 'in',
                    'options': [{
                        'name': 'data',
                        'value': ['PUBLISHED']
                    }]
                }
            }

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

    def get_account_billing_items(self, mask=None):
        """Gets all the topLevelBillingItems currently active on the account

        :param string mask: Object Mask
        :return: Billing_Item
        """

        if mask is None:
            mask = """mask[
                orderItem[id,order[id,userRecord[id,email,displayName,userStatus]]],
                nextInvoiceTotalRecurringAmount,
                location, hourlyFlag
            ]"""

        object_filter = {
            "allTopLevelBillingItems": {
                "cancellationDate": {
                    "operation": "is null"
                },
                "createDate": utils.query_filter_orderby()
            }
        }

        return self.client.call('Account', 'getAllTopLevelBillingItems',
                                mask=mask, filter=object_filter, iter=True, limit=100)

    def get_billing_item(self, identifier, mask=None):
        """Gets details about a billing item

        :param int identifier: Billing_Item id
        :param string mask: Object mask to use.
        :return: Billing_Item
        """

        if mask is None:
            mask = self._DEFAULT_BILLING_ITEM_MASK

        return self.client.call('Billing_Item', 'getObject', id=identifier, mask=mask)

    def get_billing_item_from_invoice(self, identifier, mask=None):
        """Gets details about a billing item of a billing invoice item

        :param int identifier: Billing_Invoice_Item id
        :param mask: Object mask to use.
        :return: Billing_Item
        """
        if mask is None:
            mask = self._DEFAULT_BILLING_ITEM_MASK
        return self.client.call('Billing_Invoice_Item', 'getBillingItem', id=identifier, mask=mask)

    def get_item_detail(self, identifier):
        """Gets details about a billing item

        :param int identifier: Billing_Item id or Billing_Invoice_Item
        :return: Billing_Item
        """

        try:
            return self.get_billing_item(identifier)
        except SoftLayerAPIError as exception:
            if exception.faultCode == 404:
                return self.get_billing_item_from_invoice(identifier)
            raise

    def cancel_item(self, identifier, reason="No longer needed", note=None):
        """Cancels a specific billing item with a reason

        :param int identifier: Billing_Item id
        :param string reason: A cancellation reason
        :param string note: Custom note to set when cancelling. Defaults to information about who canceled the item.
        :return: bool
        """

        if note is None:
            user = self.client.call('Account', 'getCurrentUser', mask="mask[id,displayName,email,username]")
            note = "Cancelled by {} with the SLCLI".format(user.get('username'))

        return self.client.call('Billing_Item', 'cancelItem', False, True, reason, note, id=identifier)

    def get_account_all_billing_orders(self, limit=100, mask=None):
        """Gets all the topLevelBillingItems currently active on the account

        :param string mask: Object Mask
        :return: Billing_Item
        """

        if mask is None:
            mask = """
                  orderTotalAmount, userRecord,
                  initialInvoice[id,amount,invoiceTotalAmount],
                  items[description]
               """
        return self.client.call('Billing_Order', 'getAllObjects',
                                limit=limit, mask=mask)

    def get_routers(self, mask=None, location=None):
        """Gets all the routers currently active on the account

        :param string mask: Object Mask
        :param string location: location string
        :returns: Routers
        """
        object_filter = ''
        if location:
            object_filter = {
                'routers': {
                    'topLevelLocation': {'name': {'operation': location}}
                }
            }

        return self.client['SoftLayer_Account'].getRouters(filter=object_filter, mask=mask)
