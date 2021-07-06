"""
    SoftLayer.tests.CLI.modules.licenses_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""

from SoftLayer.fixtures import SoftLayer_Product_Order

from SoftLayer.fixtures import SoftLayer_Product_Package
from SoftLayer import testing


class LicensesTests(testing.TestCase):

    def test_create(self):
        _mock = self.set_mock('SoftLayer_Product_Package', 'getItems')

        _mock.return_value = SoftLayer_Product_Package.getItems_vmware

        order_mock = self.set_mock('SoftLayer_Product_Order', 'placeOrder')
        order_mock.return_value = SoftLayer_Product_Order.wmware_placeOrder
        result = self.run_command(['licenses',
                                   'create',
                                   '-k', 'VMWARE_VSAN_ENTERPRISE_TIER_III_65_124_TB_6_X_2',
                                   '-d dal03'])
        self.assert_no_fail(result)

    def test_cancel(self):
        result = self.run_command(['licenses',
                                   'cancel',
                                   'ABCDE-6CJ8L-J8R9H-000R0-CDR70',
                                   '--immediate'])
        result = self.run_command(['licenses', 'create-options'])
        self.assert_no_fail(result)
