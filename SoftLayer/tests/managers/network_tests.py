"""
    SoftLayer.tests.managers.network_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import SoftLayer
from SoftLayer import fixtures
from SoftLayer import testing


class NetworkTests(testing.TestCase):

    def set_up(self):
        self.network = SoftLayer.NetworkManager(self.client)

    def test_ip_lookup(self):
        result = self.network.ip_lookup('10.0.1.37')

        expected = fixtures.SoftLayer_Network_Subnet_IpAddress.getByIpAddress
        self.assertEqual(result, expected)
        self.assert_called_with('SoftLayer_Network_Subnet_IpAddress',
                                'getByIpAddress',
                                args=('10.0.1.37',))

    def test_add_subnet_raises_exception_on_failure(self):
        self.assertRaises(TypeError, self.network.add_subnet, ('bad'))

    def test_add_global_ip(self):
        # Test a global IPv4 order
        result = self.network.add_global_ip(test_order=True)

        self.assertEqual(fixtures.SoftLayer_Product_Order.verifyOrder, result)

    def test_add_subnet_for_ipv4(self):
        # Test a four public address IPv4 order
        result = self.network.add_subnet('public',
                                         quantity=4,
                                         vlan_id=1234,
                                         version=4,
                                         test_order=True)

        self.assertEqual(fixtures.SoftLayer_Product_Order.verifyOrder, result)

        result = self.network.add_subnet('public',
                                         quantity=4,
                                         vlan_id=1234,
                                         version=4,
                                         test_order=False)

        self.assertEqual(fixtures.SoftLayer_Product_Order.verifyOrder, result)

        result = self.network.add_subnet('global',
                                         test_order=True)

        self.assertEqual(fixtures.SoftLayer_Product_Order.verifyOrder, result)

    def test_add_subnet_for_ipv6(self):
        # Test a public IPv6 order
        result = self.network.add_subnet('public',
                                         quantity=64,
                                         vlan_id=45678,
                                         version=6,
                                         test_order=True)

        self.assertEqual(fixtures.SoftLayer_Product_Order.verifyOrder, result)

        # Test a global IPv6 order
        result = self.network.add_subnet('global',
                                         version=6,
                                         test_order=True)

        self.assertEqual(fixtures.SoftLayer_Product_Order.verifyOrder, result)

    def test_assign_global_ip(self):
        result = self.network.assign_global_ip(9876, '172.16.24.76')

        self.assertEqual(result, True)
        self.assert_called_with('SoftLayer_Network_Subnet_IpAddress_Global',
                                'route',
                                identifier=9876,
                                args=('172.16.24.76',))

    def test_cancel_global_ip(self):
        result = self.network.cancel_global_ip(1234)

        self.assertEqual(result, True)
        self.assert_called_with('SoftLayer_Billing_Item', 'cancelService',
                                identifier=1234)

    def test_cancel_subnet(self):
        result = self.network.cancel_subnet(1234)

        self.assertEqual(result, True)
        self.assert_called_with('SoftLayer_Billing_Item', 'cancelService',
                                identifier=1056)

    def test_edit_rwhois(self):
        result = self.network.edit_rwhois(
            abuse_email='abuse@test.foo',
            address1='123 Test Street',
            address2='Apt. #31',
            city='Anywhere',
            company_name='TestLayer',
            country='US',
            first_name='Bob',
            last_name='Bobinson',
            postal_code='9ba62',
            private_residence=False,
            state='TX')

        self.assertEqual(result, True)
        expected = {
            'abuseEmail': 'abuse@test.foo',
            'address1': '123 Test Street',
            'address2': 'Apt. #31',
            'city': 'Anywhere',
            'companyName': 'TestLayer',
            'country': 'US',
            'firstName': 'Bob',
            'lastName': 'Bobinson',
            'postalCode': '9ba62',
            'privateResidenceFlag': False,
            'state': 'TX',
        }
        self.assert_called_with('SoftLayer_Network_Subnet_Rwhois_Data',
                                'editObject',
                                identifier='id',
                                args=(expected,))

    def test_get_rwhois(self):
        result = self.network.get_rwhois()

        self.assertEqual(result, fixtures.SoftLayer_Account.getRwhoisData)
        self.assert_called_with('SoftLayer_Account', 'getRwhoisData')

    def test_get_subnet(self):
        result = self.network.get_subnet(9876)

        self.assertEqual(result, fixtures.SoftLayer_Network_Subnet.getObject)
        self.assert_called_with('SoftLayer_Network_Subnet', 'getObject',
                                identifier=9876)

    def test_get_vlan(self):
        result = self.network.get_vlan(1234)

        self.assertEqual(result, fixtures.SoftLayer_Network_Vlan.getObject)
        self.assert_called_with('SoftLayer_Network_Vlan', 'getObject',
                                identifier=1234)

    def test_list_global_ips_default(self):
        result = self.network.list_global_ips()

        self.assertEqual(result,
                         fixtures.SoftLayer_Account.getGlobalIpRecords)
        mask = 'mask[destinationIpAddress[hardware, virtualGuest],ipAddress]'
        self.assert_called_with('SoftLayer_Account', 'getGlobalIpRecords',
                                mask=mask)

    def test_list_global_ips_with_filter(self):
        result = self.network.list_global_ips(version=4)

        self.assertEqual(result,
                         fixtures.SoftLayer_Account.getGlobalIpRecords)
        mask = 'mask[destinationIpAddress[hardware, virtualGuest],ipAddress]'
        _filter = {
            'globalIpRecords': {
                'ipAddress': {
                    'subnet': {
                        'version': {'operation': 4},
                    }
                }
            }
        }
        mask = 'mask[destinationIpAddress[hardware, virtualGuest],ipAddress]'
        self.assert_called_with('SoftLayer_Account', 'getGlobalIpRecords',
                                mask=mask,
                                filter=_filter)

    def test_list_subnets_default(self):
        result = self.network.list_subnets()

        self.assertEqual(result, fixtures.SoftLayer_Account.getSubnets)
        _filter = {'subnets': {'subnetType': {'operation': '!= GLOBAL_IP'}}}
        mask = 'mask[hardware,datacenter,ipAddressCount,virtualGuests]'
        self.assert_called_with('SoftLayer_Account', 'getSubnets',
                                mask=mask,
                                filter=_filter)

    def test_list_subnets_with_filters(self):
        result = self.network.list_subnets(
            identifier='10.0.0.1',
            datacenter='dal00',
            subnet_type='PRIMARY',
            version=4,
        )

        self.assertEqual(result, fixtures.SoftLayer_Account.getSubnets)
        _filter = {
            'subnets': {
                'datacenter': {
                    'name': {'operation': '_= dal00'}
                },
                'version': {'operation': 4},
                'subnetType': {'operation': '_= PRIMARY'},
                'networkIdentifier': {'operation': '_= 10.0.0.1'}
            }
        }
        mask = 'mask[hardware,datacenter,ipAddressCount,virtualGuests]'
        self.assert_called_with('SoftLayer_Account', 'getSubnets',
                                mask=mask,
                                filter=_filter)

    def test_list_vlans_default(self):
        result = self.network.list_vlans()

        self.assertEqual(result, fixtures.SoftLayer_Account.getNetworkVlans)
        self.assert_called_with('SoftLayer_Account', 'getNetworkVlans')

    def test_list_vlans_with_filters(self):
        result = self.network.list_vlans(
            vlan_number=5,
            datacenter='dal00',
            name='primary-vlan',
        )

        self.assertEqual(result, fixtures.SoftLayer_Account.getNetworkVlans)
        _filter = {
            'networkVlans': {
                'primaryRouter': {
                    'datacenter': {
                        'name': {'operation': '_= dal00'}},
                },
                'vlanNumber': {'operation': 5},
                'name': {'operation': '_= primary-vlan'},
            },
        }
        self.assert_called_with('SoftLayer_Account', 'getNetworkVlans',
                                filter=_filter)

    def test_summary_by_datacenter(self):
        result = self.network.summary_by_datacenter()

        expected = {'dal00': {'hardwareCount': 1,
                              'networkingCount': 1,
                              'virtualGuestCount': 1,
                              'subnetCount': 0,
                              'primaryIpCount': 6,
                              'vlanCount': 3}}
        self.assertEqual(expected, result)

    def test_resolve_global_ip_ids(self):
        _id = self.network.resolve_global_ip_ids('10.0.0.1')
        self.assertEqual(_id, ['200', '201'])

    def test_resolve_global_ip_ids_no_results(self):
        mock = self.set_mock('SoftLayer_Account', 'getGlobalIpRecords')
        mock.return_value = []

        _id = self.network.resolve_global_ip_ids('nope')

        self.assertEqual(_id, [])

    def test_resolve_subnet_ids(self):
        _id = self.network.resolve_subnet_ids('10.0.0.1/29')
        self.assertEqual(_id, ['100'])

    def test_resolve_subnet_ids_no_results(self):
        mock = self.set_mock('SoftLayer_Account', 'getSubnets')
        mock.return_value = []

        _id = self.network.resolve_subnet_ids('nope')

        self.assertEqual(_id, [])

    def test_resolve_vlan_ids(self):
        mock = self.set_mock('SoftLayer_Account', 'getNetworkVlans')
        mock.return_value = [{'id': '100'}]

        _id = self.network.resolve_vlan_ids('vlan_name')
        self.assertEqual(_id, ['100'])

    def test_resolve_vlan_ids_no_results(self):
        mock = self.set_mock('SoftLayer_Account', 'getNetworkVlans')
        mock.return_value = []

        _id = self.network.resolve_vlan_ids('nope')

        self.assertEqual(_id, [])

    def test_unassign_global_ip(self):
        result = self.network.unassign_global_ip(9876)

        self.assertEqual(result, True)
        self.assert_called_with('SoftLayer_Network_Subnet_IpAddress_Global',
                                'unroute',
                                identifier=9876)
