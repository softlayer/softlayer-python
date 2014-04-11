"""
    SoftLayer.tests.managers.network_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
from SoftLayer import NetworkManager
from SoftLayer.tests import unittest, FixtureClient
from SoftLayer.tests.fixtures import Product_Order

from mock import ANY, call


class NetworkTests(unittest.TestCase):

    def setUp(self):
        self.client = FixtureClient()
        self.network = NetworkManager(self.client)

    def test_ip_lookup(self):
        service = self.client['Network_Subnet_IpAddress']

        self.network.ip_lookup('10.0.1.37')
        service.getByIpAddress.assert_called_with('10.0.1.37', mask=ANY)

    def test_add_subnet_raises_exception_on_failure(self):
        self.assertRaises(TypeError, self.network.add_subnet, ('bad'))

    def test_add_global_ip(self):
        # Test a global IPv4 order
        result = self.network.add_global_ip(test_order=True)

        self.assertEqual(Product_Order.verifyOrder, result)

    def test_add_subnet_for_ipv4(self):
        # Test a four public address IPv4 order
        result = self.network.add_subnet('public',
                                         quantity=4,
                                         vlan_id=1234,
                                         version=4,
                                         test_order=True)

        self.assertEqual(Product_Order.verifyOrder, result)

        result = self.network.add_subnet('public',
                                         quantity=4,
                                         vlan_id=1234,
                                         version=4,
                                         test_order=False)

        self.assertEqual(Product_Order.verifyOrder, result)

        result = self.network.add_subnet('global',
                                         test_order=True)

        self.assertEqual(Product_Order.verifyOrder, result)

    def test_add_subnet_for_ipv6(self):
        # Test a public IPv6 order
        result = self.network.add_subnet('public',
                                         quantity=64,
                                         vlan_id=45678,
                                         version=6,
                                         test_order=True)

        self.assertEqual(Product_Order.verifyOrder, result)

        # Test a global IPv6 order
        result = self.network.add_subnet('global',
                                         version=6,
                                         test_order=True)

        self.assertEqual(Product_Order.verifyOrder, result)

    def test_assign_global_ip(self):
        self.network.assign_global_ip(9876, '172.16.24.76')

        service = self.client['Network_Subnet_IpAddress_Global']
        service.route.assert_called_with('172.16.24.76', id=9876)

    def test_cancel_global_ip(self):
        self.network.cancel_global_ip(1234)

        service = self.client['Billing_Item']
        service.cancelService.assert_called_with(id=1234)

    def test_cancel_subnet(self):
        self.network.cancel_subnet(1234)

        service = self.client['Billing_Item']
        service.cancelService.assert_called_with(id=1056)

    def test_edit_rwhois(self):
        self.network.edit_rwhois(
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
        f = self.client['Network_Subnet_Rwhois_Data'].editObject
        f.assert_called_with(expected, id='id')

    def test_get_rwhois(self):
        self.network.get_rwhois()
        self.client['Account'].getRwhoisData.assert_called()

    def test_get_subnet(self):
        mcall = call(id=9876, mask=ANY)
        service = self.client['Network_Subnet']

        self.network.get_subnet(9876)
        service.getObject.assert_has_calls(mcall)

    def test_get_vlan(self):
        service = self.client['Network_Vlan']

        self.network.get_vlan(1234)
        service.getObject.assert_has_calls(call(id=1234, mask=ANY))

    def test_list_global_ips_default(self):
        self.network.list_global_ips()

        mask = 'destinationIpAddress[hardware, virtualGuest],ipAddress'
        service = self.client['Account']
        service.getGlobalIpRecords.assert_has_calls(call(filter={}, mask=mask))

    def test_list_global_ips_with_filter(self):
        self.network.list_global_ips(version=4)

        mask = 'destinationIpAddress[hardware, virtualGuest],ipAddress'
        _filter = {
            'globalIpRecords': {
                'ipAddress': {
                    'subnet': {
                        'version': {'operation': 4},
                    }
                }
            }
        }
        service = self.client['Account']
        service.getGlobalIpRecords.assert_has_calls(call(filter=_filter,
                                                         mask=mask))

    def test_list_subnets_default(self):
        _filter = {'subnets': {'subnetType': {'operation': '!= GLOBAL_IP'}}}
        mask = 'hardware,datacenter,ipAddressCount,virtualGuests'
        service = self.client['Account']

        self.network.list_subnets()

        service.getSubnets.assert_has_calls(call(filter=_filter, mask=mask))

    def test_list_subnets_with_filters(self):
        result = self.network.list_subnets(
            identifier='10.0.0.1',
            datacenter='dal00',
            subnet_type='PRIMARY',
            version=4,
        )

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
        mask = 'hardware,datacenter,ipAddressCount,virtualGuests'
        self.client['Account'].getSubnets.assert_called_with(filter=_filter,
                                                             mask=mask)
        self.assertEqual(self.client['Account'].getSubnets.return_value,
                         result)

    def test_list_vlans_default(self):
        service = self.client['Account']

        self.network.list_vlans()
        service.getNetworkVlans.assert_has_calls(call(filter={}, mask=ANY))

    def test_list_vlans_with_filters(self):
        self.network.list_vlans(
            vlan_number=5,
            datacenter='dal00',
            name='primary-vlan',
        )

        service = self.client['Account']
        service.getNetworkVlans.assert_has_calls(call(
            filter={
                'networkVlans': {
                    'primaryRouter': {
                        'datacenter': {
                            'name': {'operation': '_= dal00'}},
                    },
                    'vlanNumber': {'operation': 5},
                    'name': {'operation': '_= primary-vlan'},
                },
            },
            mask=ANY
        ))

    def test_summary_by_datacenter(self):
        result = self.network.summary_by_datacenter()

        expected = {
            'dal00': {
                'hardwareCount': 1,
                'networkingCount': 1,
                'primaryIpCount': 3,
                'subnetCount': 0,
                'virtualGuestCount': 1,
                'vlanCount': 1
            }}
        self.assertEqual(expected, result)

    def test_resolve_global_ip_ids(self):
        service = self.client['Account']
        _id = self.network.resolve_global_ip_ids('10.0.0.1')
        self.assertEqual(_id, ['200'])

        service.getGlobalIpRecords.return_value = []
        _id = self.network.resolve_global_ip_ids('nope')
        self.assertEqual(_id, [])

    def test_resolve_subnet_ids(self):
        service = self.client['Account']

        _id = self.network.resolve_subnet_ids('10.0.0.1/29')
        self.assertEqual(_id, ['100'])

        service.getSubnets.return_value = []
        _id = self.network.resolve_subnet_ids('nope')
        self.assertEqual(_id, [])

    def test_resolve_vlan_ids(self):
        service = self.client['Account']
        service.getNetworkVlans.side_effect = [[{'id': '100'}], []]

        _id = self.network.resolve_vlan_ids('vlan_name')
        self.assertEqual(_id, ['100'])

        _id = self.network.resolve_vlan_ids('nope')
        self.assertEqual(_id, [])

    def test_unassign_global_ip(self):
        self.network.unassign_global_ip(9876)

        service = self.client['Network_Subnet_IpAddress_Global']
        service.unroute.assert_called_with(id=9876)
