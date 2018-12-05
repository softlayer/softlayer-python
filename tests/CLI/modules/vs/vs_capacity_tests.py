"""
    SoftLayer.tests.CLI.modules.vs_capacity_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
from SoftLayer.fixtures import SoftLayer_Product_Order
from SoftLayer.fixtures import SoftLayer_Product_Package
from SoftLayer import testing


class VSCapacityTests(testing.TestCase):

    def test_list(self):
        result = self.run_command(['vs', 'capacity', 'list'])
        self.assert_no_fail(result)

    def test_detail(self):
        result = self.run_command(['vs', 'capacity', 'detail', '1234'])
        self.assert_no_fail(result)

    def test_detail_pending(self):
        # Instances don't have a billing item if they haven't been approved yet.
        capacity_mock = self.set_mock('SoftLayer_Virtual_ReservedCapacityGroup', 'getObject')
        get_object = {
            'name': 'test-capacity',
            'instances': [
                {
                    'createDate': '2018-09-24T16:33:09-06:00',
                    'guestId': 62159257,
                    'id': 3501,
                }
            ]
        }
        capacity_mock.return_value = get_object
        result = self.run_command(['vs', 'capacity', 'detail', '1234'])
        self.assert_no_fail(result)

    def test_create_test(self):
        item_mock = self.set_mock('SoftLayer_Product_Package', 'getItems')
        item_mock.return_value = SoftLayer_Product_Package.getItems_RESERVED_CAPACITY
        order_mock = self.set_mock('SoftLayer_Product_Order', 'verifyOrder')
        order_mock.return_value = SoftLayer_Product_Order.rsc_verifyOrder
        result = self.run_command(['vs', 'capacity', 'create', '--name=TEST', '--test',
                                   '--backend_router_id=1234', '--flavor=B1_1X2_1_YEAR_TERM', '--instances=10'])
        self.assert_no_fail(result)

    def test_create(self):
        item_mock = self.set_mock('SoftLayer_Product_Package', 'getItems')
        item_mock.return_value = SoftLayer_Product_Package.getItems_RESERVED_CAPACITY
        order_mock = self.set_mock('SoftLayer_Product_Order', 'placeOrder')
        order_mock.return_value = SoftLayer_Product_Order.rsc_placeOrder
        result = self.run_command(['vs', 'capacity', 'create', '--name=TEST', '--instances=10',
                                   '--backend_router_id=1234', '--flavor=B1_1X2_1_YEAR_TERM'])
        self.assert_no_fail(result)

    def test_create_options(self):
        result = self.run_command(['vs', 'capacity', 'create_options'])
        self.assert_no_fail(result)

    def test_create_guest_test(self):
        result = self.run_command(['vs', 'capacity', 'create-guest', '--capacity-id=3103', '--primary-disk=25',
                                   '-H ABCDEFG', '-D test_list.com', '-o UBUNTU_LATEST_64', '-kTest 1', '--test'])
        self.assert_no_fail(result)

    def test_create_guest(self):
        order_mock = self.set_mock('SoftLayer_Product_Order', 'placeOrder')
        order_mock.return_value = SoftLayer_Product_Order.rsi_placeOrder
        result = self.run_command(['vs', 'capacity', 'create-guest', '--capacity-id=3103', '--primary-disk=25',
                                   '-H ABCDEFG', '-D test_list.com', '-o UBUNTU_LATEST_64', '-kTest 1'])
        self.assert_no_fail(result)
