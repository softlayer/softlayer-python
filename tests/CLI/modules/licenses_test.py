from SoftLayer.fixtures import SoftLayer_Product_Package
from SoftLayer import testing


class LicensesTests(testing.TestCase):

    def test_create(self):
        _mock = self.set_mock('SoftLayer_Product_Package', 'getItems')

        _mock.return_value = SoftLayer_Product_Package.getItems_vmware

        result = self.run_command(['licenses', 'create-options'])
        self.assert_no_fail(result)
