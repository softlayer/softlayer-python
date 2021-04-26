"""
    SoftLayer.tests.CLI.modules.subnet_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import json
from unittest import mock as mock

import SoftLayer
from SoftLayer.fixtures import SoftLayer_Product_Order
from SoftLayer.fixtures import SoftLayer_Product_Package
from SoftLayer import testing


class SubnetTests(testing.TestCase):

    def test_detail(self):
        result = self.run_command(['subnet', 'detail', '1234'])
        subnet = json.loads(result.output)
        self.assert_no_fail(result)
        self.assertEqual(subnet.get('id'), 1234)
        self.assertEqual(subnet.get('identifier'), '1.2.3.4/26')

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

    @mock.patch('SoftLayer.CLI.subnet.edit.click')
    def test_subnet_set_tags(self, click):
        result = self.run_command(['subnet', 'edit', '1234', '--tags=tag1,tag2'])
        click.secho.assert_called_with('Set tags successfully', fg='green')
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Network_Subnet', 'setTags', identifier=1234, args=("tag1,tag2",))

    @mock.patch('SoftLayer.CLI.subnet.edit.click')
    def test_subnet_edit_note(self, click):
        result = self.run_command(['subnet', 'edit', '1234', '--note=test'])
        click.secho.assert_called_with('Edit note successfully', fg='green')
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Network_Subnet', 'editNote', identifier=1234, args=("test",))

    @mock.patch('SoftLayer.CLI.subnet.edit.click')
    def test_subnet_set_tags_failure(self, click):
        mock = self.set_mock('SoftLayer_Network_Subnet', 'setTags')
        mock.return_value = False
        result = self.run_command(['subnet', 'edit', '1234', '--tags=tag1,tag2'])
        click.secho.assert_called_with('Failed to set tags', fg='red')
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Network_Subnet', 'setTags', identifier=1234, args=("tag1,tag2",))

    @mock.patch('SoftLayer.CLI.subnet.edit.click')
    def test_edit_note_failure(self, click):
        mock = self.set_mock('SoftLayer_Network_Subnet', 'editNote')
        mock.return_value = False
        result = self.run_command(['subnet', 'edit', '1234', '--note=test'])
        click.secho.assert_called_with('Failed to edit note', fg='red')
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Network_Subnet', 'editNote', identifier=1234, args=("test",))

    def test_editrou_Ip(self):
        result = self.run_command(['subnet', 'edit-ip', '16.26.26.26', '--note=test'])
        self.assert_no_fail(result)
        self.assertTrue(result)

    def test_editrou_Id(self):
        result = self.run_command(['subnet', 'edit-ip', '123456', '--note=test'])
        self.assert_no_fail(result)
        self.assertTrue(result)

    def test_lookup(self):
        result = self.run_command(['subnet', 'lookup', '1.2.3.10'])
        self.assert_no_fail(result)
        self.assertEqual(json.loads(result.output), {'device': {
            'id': 12856,
            'name': 'unit.test.com',
            'type': 'server'},
            "id": 12345,
            "ip": "10.0.1.37",
            "subnet": {
                "id": 258369,
                "identifier": "10.0.1.38/26",
                "netmask": "255.255.255.192",
                "gateway": "10.47.16.129",
                "type": "PRIMARY"
        }})

    @mock.patch('SoftLayer.CLI.formatting.no_going_back')
    def test_cancel(self, confirm_mock):
        confirm_mock.return_value = True
        result = self.run_command(['subnet', 'cancel', '1234'])
        self.assert_no_fail(result)

    def test_cancel_fail(self):
        result = self.run_command(['subnet', 'cancel', '1234'])
        self.assertEqual(result.exit_code, 2)
