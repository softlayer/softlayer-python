"""
    SoftLayer.license
    ~~~~~~~~~~~~~~~
    License Manager

    :license: MIT, see LICENSE for more details.
"""


# pylint: disable=too-many-public-methods


class LicensesManager(object):
    """Manages account lincese."""

    def __init__(self, client):
        self.client = client

    def get_all_objects(self):
        """Show the all VM ware licenses of account.

         """
        _mask = '''softwareDescription,billingItem'''

        return self.client.call('SoftLayer_Software_AccountLicense',
                                'getAllObjects', mask=_mask)

    def cancel_item(self, identifier, cancel_immediately,
                    reason_cancel, customer_note):
        """Cancel a billing item immediately, deleting all its data.

        :param integer identifier: the instance ID to cancel
        :param string reason_cancel: reason cancel
        """
        return self.client.call('SoftLayer_Billing_Item', 'cancelItem',
                                cancel_immediately,
                                True,
                                reason_cancel,
                                customer_note,
                                id=identifier)
