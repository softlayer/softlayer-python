"""
    SoftLayer.tests.CLI.modules.vlan_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import json
from unittest import mock as mock

from SoftLayer.fixtures import SoftLayer_Product_Order
from SoftLayer.fixtures import SoftLayer_Product_Package
from SoftLayer import testing


class VlanTests(testing.TestCase):

    def test_detail(self):
        result = self.run_command(['vlan', 'detail', '1234'])
        self.assert_no_fail(result)

    def test_detail_no_vs(self):
        result = self.run_command(['vlan', 'detail', '1234', '--no-vs'])
        self.assert_no_fail(result)

    def test_detail_no_hardware(self):
        result = self.run_command(['vlan', 'detail', '1234', '--no-hardware'])
        self.assert_no_fail(result)

    def test_subnet_list(self):
        vlan_mock = self.set_mock('SoftLayer_Network_Vlan', 'getObject')
        getObject = {
            'primaryRouter': {
                'datacenter': {'id': 1234, 'longName': 'TestDC'},
                'fullyQualifiedDomainName': 'fcr01.TestDC'
            },
            'id': 1234,
            'vlanNumber': 4444,
            'firewallInterfaces': None,
            'subnets': [
                {
                    'id': 99,
                    'networkIdentifier': 1111111,
                    'netmask': '255.255.255.0',
                    'gateway': '12.12.12.12',
                    'subnetType': 'TEST',
                    'usableIpAddressCount': 1

                }

            ]
        }
        vlan_mock.return_value = getObject
        result = self.run_command(['vlan', 'detail', '1234'])
        self.assert_no_fail(result)

    def test_detail_hardware_without_hostname(self):
        vlan_mock = self.set_mock('SoftLayer_Network_Vlan', 'getObject')
        getObject = {
            'primaryRouter': {
                'datacenter': {'id': 1234, 'longName': 'TestDC'},
                'fullyQualifiedDomainName': 'fcr01.TestDC'
            },
            'id': 1234,
            'vlanNumber': 4444,
            'firewallInterfaces': None,
            'subnets': [],
            'hardware': [
                {'a_hardware': 'that_has_none_of_the_expected_attributes_provided'},
                {'domain': 'example.com',
                 'networkManagementIpAddress': '10.171.202.131',
                 'hardwareStatus': {'status': 'ACTIVE', 'id': 5},
                 'notes': '',
                 'hostname': 'hw1', 'hardwareStatusId': 5,
                 'globalIdentifier': 'f6ea716a-41d8-4c52-bb2e-48d63105f4b0',
                 'primaryIpAddress': '169.60.169.169',
                 'primaryBackendIpAddress': '10.171.202.130', 'id': 826425,
                 'privateIpAddress': '10.171.202.130',
                 'fullyQualifiedDomainName': 'hw1.example.com'}
            ]
        }
        vlan_mock.return_value = getObject
        result = self.run_command(['vlan', 'detail', '1234'])
        self.assert_no_fail(result)

    @mock.patch('SoftLayer.CLI.vlan.edit.click')
    def test_vlan_edit(self, click):
        result = self.run_command(['vlan', 'edit', '--name=nameTest', '--note=noteTest', '--tags=tag1,tag2', '100'])
        click.secho.assert_called_with('Vlan edited successfully', fg='green')
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Network_Vlan', 'editObject', identifier=100)

    @mock.patch('SoftLayer.CLI.vlan.edit.click')
    def test_vlan_edit_failure(self, click):
        mock = self.set_mock('SoftLayer_Network_Vlan', 'editObject')
        mock.return_value = False
        result = self.run_command(['vlan', 'edit', '--name=nameTest', '--note=noteTest', '--tags=tag1,tag2', '100'])
        click.secho.assert_called_with('Failed to edit the vlan', fg='red')
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Network_Vlan', 'editObject', identifier=100)

    def test_vlan_detail_firewall(self):
        vlan_mock = self.set_mock('SoftLayer_Network_Vlan', 'getObject')
        get_object = {
            'primaryRouter': {
                'datacenter': {'id': 1234, 'longName': 'TestDC'},
                'fullyQualifiedDomainName': 'fcr01.TestDC'
            },
            'id': 1234,
            'vlanNumber': 4444,
            'networkVlanFirewall': {
                'datacenter': {'id': 1234, 'longName': 'TestDC'},
                'fullyQualifiedDomainName': 'fcr01.TestDC'
            },
        }
        vlan_mock.return_value = get_object
        result = self.run_command(['vlan', 'detail', '1234'])
        self.assert_no_fail(result)

    def test_vlan_detail_gateway(self):
        vlan_mock = self.set_mock('SoftLayer_Network_Vlan', 'getObject')
        get_object = {
            'primaryRouter': {
                'datacenter': {'id': 1234, 'longName': 'TestDC'},
                'fullyQualifiedDomainName': 'fcr01.TestDC'
            },
            'id': 1234,
            'vlanNumber': 4444,
            'attachedNetworkGateway': {
                'id': 54321,
                "name": 'support'
            },
        }
        vlan_mock.return_value = get_object
        result = self.run_command(['vlan', 'detail', '1234'])
        self.assert_no_fail(result)

    def test_vlan_list(self):
        result = self.run_command(['vlan', 'list'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Account', 'getNetworkVlans')

    def test_create_vlan(self):
        _mock = self.set_mock('SoftLayer_Product_Package', 'getItems')
        _mock.return_value = SoftLayer_Product_Package.getItemsVLAN

        order_mock = self.set_mock('SoftLayer_Product_Order', 'placeOrder')
        order_mock.return_value = SoftLayer_Product_Order.vlan_placeOrder

        result = self.run_command(['vlan', 'create',
                                   '--name', 'test',
                                   '-d TEST00',
                                   '--network', 'public',
                                   '--billing', 'hourly'
                                   ])

        self.assert_no_fail(result)
        self.assertEqual(json.loads(result.output),
                         {'id': 123456, 'created': '2021-06-02 15:23:47', 'name': 'test'})

    def test_create_vlan_pod(self):
        _mock = self.set_mock('SoftLayer_Product_Package', 'getItems')
        _mock.return_value = SoftLayer_Product_Package.getItemsVLAN

        order_mock = self.set_mock('SoftLayer_Product_Order', 'placeOrder')
        order_mock.return_value = SoftLayer_Product_Order.vlan_placeOrder

        result = self.run_command(['vlan', 'create',
                                   '--name', 'test',
                                   '-p', 'TEST00.pod2',
                                   '--network', 'public',
                                   '--billing', 'hourly'
                                   ])

        self.assert_no_fail(result)
        self.assertEqual(json.loads(result.output),
                         {'id': 123456, 'created': '2021-06-02 15:23:47', 'name': 'test'})

    @mock.patch('SoftLayer.CLI.formatting.no_going_back')
    def test_vlan_cancel(self, confirm_mock):
        confirm_mock.return_value = True
        mock = self.set_mock('SoftLayer_Network_Vlan', 'getCancelFailureReasons')
        mock.return_value = []
        result = self.run_command(['vlan', 'cancel', '1234'])
        self.assert_no_fail(result)

    @mock.patch('SoftLayer.CLI.formatting.no_going_back')
    def test_vlan_cancel_error(self, confirm_mock):
        confirm_mock.return_value = True
        result = self.run_command(['vlan', 'cancel', '1234'])
        self.assertTrue(result.exit_code, 2)

    @mock.patch('SoftLayer.CLI.formatting.no_going_back')
    def test_vlan_cancel_fail(self, confirm_mock):
        confirm_mock.return_value = False
        result = self.run_command(['vlan', 'cancel', '1234'])
        self.assertTrue(result.exit_code, 2)
