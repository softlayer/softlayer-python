"""
    SoftLayer.tests.CLI.modules.vlan_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
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
