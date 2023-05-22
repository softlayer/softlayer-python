"""
    SoftLayer.account
    ~~~~~~~~~~~~~~~~~~~~~~~
    Account manager

    :license: MIT, see License for more details.
"""

import logging

from SoftLayer.exceptions import SoftLayerAPIError
from SoftLayer import utils

# Invalid names are ignored due to long method names and short argument names
# pylint: disable=invalid-name

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

    def get_upcoming_events(self, event_type, date_min=None):
        """Retrieves a list of Notification_Occurrence_Events that have not ended yet

        :param: String event_type: notification event type.
        :param: String date_min: greater Than Date to data recovery, default is 2 days ago.
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

        self.add_event_filter(_filter, event_type, date_min)

        return self.client.call('Notification_Occurrence_Event', 'getAllObjects', filter=_filter, mask=mask, iter=True)

    @staticmethod
    def add_event_filter(_filter, event_type, date_min=None):
        """Add data to the object filter.

        :param: _filter: event filter.
        :param: string event_type: event type.
        :param: string date_min: greater Than Date to data recovery, default is 2 days ago.
        """

        if event_type == 'PLANNED':
            if date_min:
                _filter['endDate'] = {
                    'operation': 'greaterThanDate',
                    'options': [{
                        'name': 'date',
                        'value': [date_min]
                    }]
                }
            else:
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
            if date_min:
                _filter['modifyDate'] = {
                    'operation': 'greaterThanDate',
                    'options': [{
                        'name': 'date',
                        'value': [date_min]
                    }]
                }
            else:
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

    def get_account_billing_items(self, create=None, category=None, mask=None):
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

        if category:
            object_filter = utils.dict_merge(object_filter,
                                             {"allTopLevelBillingItems": {"categoryCode": {"operation": category}}})
        if create:
            object_filter = utils.dict_merge(object_filter,
                                             {"allTopLevelBillingItems": {"createDate": {"operation": create}}})

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

    def get_routers(self, location=None, mask=None):
        """Gets all the routers currently active on the account

        :param string mask: Object Mask
        :param string location: location string
        :returns: Routers
        """

        if mask is None:
            mask = """
                 topLevelLocation
               """
        object_filter = ''
        if location:
            object_filter = {
                'routers': {
                    'topLevelLocation': {'name': {'operation': location}}
                }
            }

        return self.client['SoftLayer_Account'].getRouters(filter=object_filter, mask=mask)

    def get_network_message_delivery_accounts(self):
        """Gets all Network Message delivery accounts.

        :returns: Network Message delivery accounts
        """

        _mask = """vendor,type"""

        return self.client['SoftLayer_Account'].getNetworkMessageDeliveryAccounts(mask=_mask)

    def get_active_virtual_licenses(self):
        """Gets all active virtual licenses account.

        :returns: active virtual licenses account
        """

        _mask = """billingItem[categoryCode,createDate,description],
                    key,id,ipAddress,
                    softwareDescription[longDescription,name,manufacturer],
                    subnet"""

        return self.client['SoftLayer_Account'].getActiveVirtualLicenses(mask=_mask)

    def get_active_account_licenses(self):
        """Gets all active account licenses.

        :returns: Active account Licenses
        """

        _mask = """billingItem,softwareDescription"""

        return self.client['SoftLayer_Account'].getActiveAccountLicenses(mask=_mask)

    def get_bandwidth_pools(self, mask=None):
        """Gets all the bandwidth pools on an account"""

        if mask is None:
            mask = """mask[totalBandwidthAllocated,locationGroup, id, name, projectedPublicBandwidthUsage,
                      billingCyclePublicBandwidthUsage[amountOut,amountIn],
                      billingItem[id,nextInvoiceTotalRecurringAmount],outboundPublicBandwidthUsage,serviceProviderId,bandwidthAllotmentTypeId,activeDetailCount]
                   """

        return self.client.call('SoftLayer_Account', 'getBandwidthAllotments', mask=mask, iter=True)

    def get_bandwidth_pool_counts(self, identifier):
        """Gets a count of all servers in a bandwidth pool

        Getting the server counts individually is significantly faster than pulling them in
        with the get_bandwidth_pools api call.
        """
        mask = "mask[id, bareMetalInstanceCount, hardwareCount, virtualGuestCount]"
        counts = self.client.call('SoftLayer_Network_Bandwidth_Version1_Allotment', 'getObject',
                                  id=identifier, mask=mask)
        total = counts.get('bareMetalInstanceCount', 0) + \
            counts.get('hardwareCount', 0) + \
            counts.get('virtualGuestCount', 0)
        return total

    def getBandwidthDetail(self, identifier):
        """Gets bandwidth pool detail.

        :returns: bandwidth pool detail
        """
        _mask = """activeDetails[allocation],projectedPublicBandwidthUsage, billingCyclePublicBandwidthUsage,
        hardware[outboundBandwidthUsage,bandwidthAllotmentDetail[allocation]],inboundPublicBandwidthUsage,
        virtualGuests[outboundPublicBandwidthUsage,bandwidthAllotmentDetail[allocation]],
        bareMetalInstances[outboundBandwidthUsage,bandwidthAllotmentDetail[allocation]]"""
        return self.client['SoftLayer_Network_Bandwidth_Version1_Allotment'].getObject(id=identifier, mask=_mask)

    def get_provisioning_scripts(self):
        """Gets a provisioning hooks.

        :returns: provisioning hook
        """

        return self.client.call('Account', 'getPostProvisioningHooks')

    def create_provisioning(self, name, uri):
        """create a provisioning script

        :param name: Name of the hook.
        :param uri: endpoint that the script will be downloaded
        """
        template = {
            'name': name,
            'uri': uri
        }
        return self.client.call('SoftLayer_Provisioning_Hook', 'createObject', template)

    def delete_provisioning(self, identifier):
        """Delete a provisioning script

        param: identifier provisioning script identifier

        Returns: boolean
        """
        return self.client.call("SoftLayer_Provisioning_Hook", "deleteObject", id=identifier)

    def get_account_upgrade_orders(self, limit=100):
        """Gets upgrade order list"""
        return self.client.call('SoftLayer_Account', 'getUpgradeRequests', limit=limit)
