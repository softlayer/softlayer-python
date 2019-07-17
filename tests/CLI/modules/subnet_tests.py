"""
    SoftLayer.tests.CLI.modules.subnet_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
from SoftLayer.fixtures import SoftLayer_Product_Order
from SoftLayer.fixtures import SoftLayer_Product_Package
from SoftLayer import testing

import json
import mock
import SoftLayer


class SubnetTests(testing.TestCase):

    def test_detail(self):
        result = self.run_command(['subnet', 'detail', '1234'])

        self.assert_no_fail(result)
        self.assertEqual(
            {
                'id': 1234,
                'identifier': '1.2.3.4/26',
                'subnet type': 'ADDITIONAL_PRIMARY',
                'network space': 'PUBLIC',
                'gateway': '1.2.3.254',
                'broadcast': '1.2.3.255',
                'datacenter': 'dal10',
                'vs': [
                    {
                        'hostname': 'hostname0',
                        'domain': 'sl.test',
                        'public_ip': '1.2.3.10',
                        'private_ip': '10.0.1.2'
                    }
                ],
                'hardware': 'none',
                'usable ips': 22
            },
            json.loads(result.output))

    def test_list(self):
        result = self.run_command(['subnet', 'list'])
        self.assert_no_fail(result)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_create_subnet_ipv4(self, confirm_mock):
        confirm_mock.return_value = True

        item_mock = self.set_mock('SoftLayer_Product_Package', 'getItems')
        item_mock.return_value = SoftLayer_Product_Package.getItems

        place_mock = self.set_mock('SoftLayer_Product_Order', 'placeOrder')
        place_mock.return_value = SoftLayer_Product_Order.placeOrder

        result = self.run_command(['subnet', 'create', 'private', '8', '12346'])
        self.assert_no_fail(result)

        output = [
            {'Item': 'Total monthly cost', 'cost': '0.00'}
        ]

        self.assertEqual(output, json.loads(result.output))

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_create_subnet_ipv6(self, confirm_mock):
        confirm_mock.return_value = True

        item_mock = self.set_mock('SoftLayer_Product_Package', 'getItems')
        item_mock.return_value = SoftLayer_Product_Package.getItems

        place_mock = self.set_mock('SoftLayer_Product_Order', 'verifyOrder')
        place_mock.return_value = SoftLayer_Product_Order.verifyOrder

        result = self.run_command(['subnet', 'create', '--v6', 'public', '64', '12346', '--test'])
        self.assert_no_fail(result)

        output = [
            {'Item': 'this is a thing', 'cost': '2.00'},
            {'Item': 'Total monthly cost', 'cost': '2.00'}
        ]

        self.assertEqual(output, json.loads(result.output))

    def test_create_subnet_no_prices_found(self):
        item_mock = self.set_mock('SoftLayer_Product_Package', 'getItems')
        item_mock.return_value = SoftLayer_Product_Package.getItems

        verify_mock = self.set_mock('SoftLayer_Product_Order', 'verifyOrder')
        verify_mock.side_effect = SoftLayer.SoftLayerAPIError('SoftLayer_Exception', 'Price not found')

        result = self.run_command(['subnet', 'create', '--v6', 'public', '32', '12346', '--test'])

        self.assertRaises(SoftLayer.SoftLayerAPIError, verify_mock)
        self.assertIn('Unable to order 32 public ipv6', result.exception.message, )

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_create_subnet_static(self, confirm_mock):
        confirm_mock.return_value = True

        item_mock = self.set_mock('SoftLayer_Product_Package', 'getItems')
        item_mock.return_value = SoftLayer_Product_Package.getItems

        place_mock = self.set_mock('SoftLayer_Product_Order', 'placeOrder')
        place_mock.return_value = SoftLayer_Product_Order.placeOrder

        result = self.run_command(['subnet', 'create', 'static', '2', '12346'])
        self.assert_no_fail(result)

        output = [
            {'Item': 'Total monthly cost', 'cost': '0.00'}
        ]

        self.assertEqual(output, json.loads(result.output))

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_create_subnet_static_ipv6(self, confirm_mock):
        confirm_mock.return_value = True

        item_mock = self.set_mock('SoftLayer_Product_Package', 'getItems')
        item_mock.return_value = SoftLayer_Product_Package.getItems

        place_mock = self.set_mock('SoftLayer_Product_Order', 'verifyOrder')
        place_mock.return_value = SoftLayer_Product_Order.verifyOrder

        result = self.run_command(['subnet', 'create', '--v6', 'static', '64', '12346', '--test'])
        self.assert_no_fail(result)

        output = [
            {'Item': 'this is a thing', 'cost': '2.00'},
            {'Item': 'Total monthly cost', 'cost': '2.00'}
        ]

        self.assertEqual(output, json.loads(result.output))
