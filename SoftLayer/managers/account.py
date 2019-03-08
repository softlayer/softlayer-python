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