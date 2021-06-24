"""
    SoftLayer.license
    ~~~~~~~~~~~~~~~
    License Manager

    :license: MIT, see LICENSE for more details.
"""

# pylint: disable=too-many-public-methods
from SoftLayer.CLI import exceptions
from SoftLayer.managers import ordering
from SoftLayer import utils


class LicensesManager(object):
    """Manages account license."""

    def __init__(self, client):
        self.client = client

    def get_all_objects(self):
        """Show the all VMware licenses of an account.

         """
        _mask = '''softwareDescription,billingItem'''

        return self.client.call('SoftLayer_Software_AccountLicense',
                                'getAllObjects', mask=_mask)

    def cancel_item(self, key, cancel_immediately=False):
        """Cancel a billing item immediately, deleting all its data.

        :param integer identifier: the instance ID to cancel
        :param string reason_cancel: reason cancel
        """
        vm_ware_licenses = self.get_all_objects()
        vm_ware_find = False
        for vm_ware in vm_ware_licenses:
            if vm_ware.get('key') == key:
                vm_ware_find = True
                self.client.call('SoftLayer_Billing_Item', 'cancelItem',
                                 cancel_immediately,
                                 True,
                                 'Cancel by cli command',
                                 'Cancel by cli command',
                                 id=utils.lookup(vm_ware, 'billingItem', 'id'))

        if not vm_ware_find:
            raise exceptions.CLIAbort(
                "Unable to find license key: {}".format(key))
        return vm_ware_find

    def create(self, datacenter, item_package):
        """Create a license

        :param string datacenter: the datacenter shortname
        :param string[] item_package: items array
        """
        complex_type = 'SoftLayer_Container_Product_Order_Software_License'
        ordering_manager = ordering.OrderingManager(self.client)
        return ordering_manager.place_order(package_keyname='SOFTWARE_LICENSE_PACKAGE',
                                            location=datacenter,
                                            item_keynames=item_package,
                                            complex_type=complex_type,
                                            hourly=False)
