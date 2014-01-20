"""
    SoftLayer.tests.managers.network_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
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
        id = 9876
        target = '172.16.24.76'

        self.network.assign_global_ip(id, target)

        service = self.client['Network_Subnet_IpAddress_Global']
        service.route.assert_called_with(target, id=id)

    def test_cancel_global_ip(self):
        service = self.client['Billing_Item']

        self.network.cancel_global_ip(1234)
        service.cancelService.assert_called_with(id=1234)

    def test_cancel_subnet(self):
        service = self.client['Billing_Item']

        self.network.cancel_subnet(1234)
        service.cancelService.assert_called_with(id=1056)

    def test_edit_rwhois(self):
        self.client['Account'].getRwhoisData.return_value = {'id': 954}

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

        f = self.client['Network_Subnet_Rwhois_Data'].editObject
        f.assert_called_with(expected, id=954)

    def test_get_rwhois(self):
        self.network.get_rwhois()
        self.client['Account'].getRwhoisData.assert_called()

    def test_get_subnet(self):
        id = 9876
        mcall = call(id=id, mask=ANY)
        service = self.client['Network_Subnet']

        self.network.get_subnet(id)
        service.getObject.assert_has_calls(mcall)

    def test_get_vlan(self):
        id = 1234
        mcall = call(id=id, mask=ANY)
        service = self.client['Network_Vlan']

        self.network.get_vlan(id)
        service.getObject.assert_has_calls(mcall)

    def test_list_global_ips_default(self):
        mask = 'mask[destinationIpAddress[hardware, virtualGuest],ipAddress]'
        mcall = call(filter={}, mask=mask)
        service = self.client['Account']

        self.network.list_global_ips()

        service.getGlobalIpRecords.assert_has_calls(mcall)

    def test_list_global_ips_with_filter(self):
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

        mcall = call(filter=_filter, mask=mask)
        service = self.client['Account']

        self.network.list_global_ips(version=4)

        service.getGlobalIpRecords.assert_has_calls(mcall)

    def test_list_subnets_default(self):
        _filter = {'subnets': {'subnetType': {'operation': 'not null'}}}
        mask = 'mask[hardware,datacenter,ipAddressCount,virtualGuests]'
        mcall = call(filter=_filter,
                     mask=mask)
        service = self.client['Account']

        self.network.list_subnets()

        service.getSubnets.assert_has_calls(mcall)

    def test_list_subnets_with_filters(self):
        identifier = '10.0.0.1'
        datacenter = 'dal00'
        subnet_type = 'PRIMARY'
        version = 4

        service = self.client['Account']
        service.getSubnets.return_value = [
            {
                'id': 100,
                'networkIdentifier': '10.0.0.1',
                'datacenter': {'name': 'dal00'},
                'version': 4,
                'subnetType': 'PRIMARY',
            },
        ]

        result = self.network.list_subnets(
            identifier=identifier,
            datacenter=datacenter,
            subnet_type=subnet_type,
            version=version,
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
        mask = 'mask[hardware,datacenter,ipAddressCount,virtualGuests]'
        service.getSubnets.assert_called_with(filter=_filter, mask=mask)

        self.assertEqual([service.getSubnets.return_value[0]], result)

    def test_list_vlans_default(self):
        mcall = call(filter={}, mask=ANY)
        service = self.client['Account']

        self.network.list_vlans()

        service.getNetworkVlans.assert_has_calls(mcall)

    def test_list_vlans_with_filters(self):
        number = 5
        datacenter = 'dal00'
        self.network.list_vlans(
            vlan_number=number,
            datacenter=datacenter,
        )

        service = self.client['Account']
        service.getNetworkVlans.assert_has_calls(call(
            filter={
                'networkVlans': {
                    'primaryRouter': {
                        'datacenter': {
                            'name': {'operation': '_= ' + datacenter}},
                    },
                    'vlanNumber': {'operation': number},
                },
            },
            mask=ANY
        ))

    def test_summary_by_datacenter(self):
        mcall = call(mask=ANY)
        service = self.client['Account']

        service.getNetworkVlans.return_value = [
            {
                'name': 'dal00',
                'hardware': [{'id': 1}],
                'networkComponents': [{'id': 2}],
                'primaryRouter': {
                    'datacenter': {'name': 'dal00'}
                },
                'totalPrimaryIpAddressCount': 3,
                'subnets': [],
                'virtualGuests': [{'id': 3}]
            }
        ]

        expected = {'dal00': {
            'hardwareCount': 1,
            'networkingCount': 1,
            'primaryIpCount': 3,
            'subnetCount': 0,
            'virtualGuestCount': 1,
            'vlanCount': 1
        }}

        result = self.network.summary_by_datacenter()

        service.getNetworkVlans.assert_has_calls(mcall)
        self.assertEqual(expected, result)

    def test_resolve_global_ip_ids(self):
        service = self.client['Account']

        _id = self.network.resolve_global_ip_ids('10.0.0.1')
        self.assertEqual(_id, '200')

        service.getGlobalIpRecords.return_value = []
        _id = self.network.resolve_global_ip_ids('nope')
        self.assertEqual(_id, None)

    def test_resolve_subnet_ids(self):
        service = self.client['Account']

        _id = self.network.resolve_subnet_ids('10.0.0.1/29')
        self.assertEqual(_id, '100')

        service.getSubnets.return_value = []
        _id = self.network.resolve_subnet_ids('nope')
        self.assertEqual(_id, None)

    def test_unassign_global_ip(self):
        id = 9876

        self.network.unassign_global_ip(id)

        service = self.client['Network_Subnet_IpAddress_Global']
        service.unroute.assert_called_with(id=id)
