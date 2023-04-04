"""
    SoftLayer.tests.CLI.modules.firewall_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import json
from unittest import mock as mock

from SoftLayer import testing


class FirewallTests(testing.TestCase):

    def test_list_firewalls(self):
        result = self.run_command(['firewall', 'list'])

        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Account', 'getNetworkGateways')

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_add_vs(self, confirm_mock):
        confirm_mock.return_value = True
        result = self.run_command(['firewall', 'add', '1000', '--firewall-type=vlan', '-ha'])
        self.assert_no_fail(result)
        self.assertIn("Firewall is being created!", result.output)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_add_vlan(self, confirm_mock):
        confirm_mock.return_value = True
        result = self.run_command(['firewall', 'add', '1000', '--firewall-type=vs'])
        self.assert_no_fail(result)
        self.assertIn("Firewall is being created!", result.output)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_add_server(self, confirm_mock):
        confirm_mock.return_value = True
        result = self.run_command(['firewall', 'add', '1000', '--firewall-type=server'])
        self.assert_no_fail(result)
        self.assertIn("Firewall is being created!", result.output)

    def test_detail_vlan_firewall(self):
        result = self.run_command(['firewall', 'detail', 'vlan:1234'])
        self.assert_no_fail(result)
        json_result = json.loads(result.output)
        self.assertEqual(json_result['rules'][0]['action'], 'permit')
        self.assertEqual(json.loads(result.output),
                         {'datacenter': 'Amsterdam 1',
                          'id': 3130,
                          'networkVlan': 'testvlan',
                          'networkVlaniD': 371028,
                          'primaryIpAddress': '192.155.239.146',
                          'rules': [{'#': 1,
                                     'action': 'permit',
                                     'dest': 'any on server:80-80',
                                     'dest_mask': '255.255.255.255',
                                     'protocol': 'tcp',
                                     'src_ip': '0.0.0.0',
                                     'src_mask': '0.0.0.0'},
                                    {'#': 2,
                                     'action': 'permit',
                                     'dest': 'any on server:1-65535',
                                     'dest_mask': '255.255.255.255',
                                     'protocol': 'tmp',
                                     'src_ip': '193.212.1.10',
                                     'src_mask': '255.255.255.255'},
                                    {'#': 3,
                                     'action': 'permit',
                                     'dest': 'any on server:80-800',
                                     'dest_mask': '255.255.255.255',
                                     'protocol': 'tcp',
                                     'src_ip': '0.0.0.0',
                                     'src_mask': '0.0.0.0'}]})

    def test_detail_multi_vlan_firewall(self):
        result = self.run_command(['firewall', 'detail', 'multiVlan:1234', '--password'])
        self.assert_no_fail(result)
        json_result = json.loads(result.output)
        self.assertEqual(json_result['rules'][0]['action'], 'permit')
        self.assertEqual(json.loads(result.output),
                         {'name': 'testFirewall',
                          'datacenter': 'Amsterdam 1',
                          'public ip': '67.228.206.245',
                          'private ip': '10.37.115.70',
                          'public  ipv6': '2607:f0d0:2703:0039:0000:0000:0000:0004',
                          'public vlan': 1255,
                          'private vlan': 1330,
                          'type': 'fortigate-security-appliance-10gb',
                          'fortiGate username': 'myusername',
                          'fortiGate password': 'test1234',
                          'rules': [{'#': 1,
                                     'action': 'permit',
                                     'dest': 'any on server:80-80',
                                     'dest_mask': '255.255.255.255',
                                     'protocol': 'tcp',
                                     'src_ip': '0.0.0.0',
                                     'src_mask': '0.0.0.0'},
                                    {'#': 2,
                                     'action': 'permit',
                                     'dest': 'any on server:1-65535',
                                     'dest_mask': '255.255.255.255',
                                     'protocol': 'tmp',
                                     'src_ip': '193.212.1.10',
                                     'src_mask': '255.255.255.255'},
                                    {'#': 3,
                                     'action': 'permit',
                                     'dest': 'any on server:80-800',
                                     'dest_mask': '255.255.255.255',
                                     'protocol': 'tcp',
                                     'src_ip': '0.0.0.0',
                                     'src_mask': '0.0.0.0'}]})

    def test_detail_vs_firewall(self):
        result = self.run_command(['firewall', 'detail', 'vs:1234'])
        self.assert_no_fail(result)
        self.assertEqual(json.loads(result.output),
                         [{'#': 1,
                           'action': 'permit',
                           'dest': 'any on server:80-80',
                           'dest_mask': '255.255.255.255',
                           'protocol': 'tcp',
                           'src_ip': '0.0.0.0',
                           'src_mask': '0.0.0.0'},
                          {'#': 2,
                           'action': 'permit',
                           'dest': 'any on server:1-65535',
                           'dest_mask': '255.255.255.255',
                           'protocol': 'tcp',
                           'src_ip': '193.212.1.10',
                           'src_mask': '255.255.255.255'},
                          {'#': 3,
                           'action': 'permit',
                           'dest': 'any on server:80-800',
                           'dest_mask': '255.255.255.255',
                           'protocol': 'tcp',
                           'src_ip': '0.0.0.0',
                           'src_mask': '0.0.0.0'}])

    def test_detail_fails(self):
        result = self.run_command(['firewall', 'detail', 'abc:1234'])
        self.assert_no_fail(result)
        expected_output = 'Invalid firewall type abc: firewall type should be either vlan, multiVlan, vs or server.\n'
        self.assertEqual(result.output, expected_output)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_cancel_firewall(self, confirm_mock):
        confirm_mock.return_value = True
        result = self.run_command(['firewall', 'cancel', 'vlan:1234'])
        self.assert_no_fail(result)
        self.assertIn("Firewall with id vlan:1234 is being cancelled!", result.output)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_edit(self, confirm_mock):
        confirm_mock.return_value = True
        result = self.run_command(['firewall', 'edit', 'vlan:1234'])
        print(result.output)

    def test_monitoring(self):
        result = self.run_command(['firewall', 'monitoring', '123456'])
        print(result.output)
