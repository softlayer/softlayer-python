"""
    SoftLayer.BillingItem
    ~~~~~~~~~~~~~~~~~~~
    BillingItem manager

    :license: MIT, see LICENSE for more details.
"""


class BillingManager(object):
    """Manager for interacting with Billing item instances."""

    def __init__(self, client):
        self.client = client

    def cancel_item(self, identifier, reason_cancel):
        """Cancel a billing item immediately, deleting all its data.

        :param integer identifier: the instance ID to cancel
        :param string reason_cancel: reason cancel
        """
        return self.client.call('SoftLayer_Billing_Item', 'cancelItem',
                                True,
                                True,
                                reason_cancel,
                                reason_cancel,
                                id=identifier)
