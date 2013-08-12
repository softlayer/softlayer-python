"""
    SoftLayer.tests.managers.network_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
    :license: BSD, see LICENSE for more details.
"""
from SoftLayer import NetworkManager
from SoftLayer.tests import unittest
from mock import MagicMock, ANY, call


class NetworkTests(unittest.TestCase):

    def setUp(self):
        self.client = MagicMock()
        self.network = NetworkManager(self.client)

    def test_ip_lookup(self):
        ip = '10.0.1.37'
        mcall = call(ip, mask=ANY)
        service = self.client['Network_Subnet_IpAddress']

        self.network.ip_lookup(ip)
        service.getByIpAddress.assert_has_calls(mcall)

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

    def test_list_subnets_default(self):
        mcall = call(filter={}, mask=ANY)
        service = self.client['Account']

        self.network.list_subnets()

        service.getSubnets.assert_has_calls(mcall)

    def test_list_subnets_with_filters(self):
        identifier = '10.0.0.1'
        datacenter = 'dal00'
        version = 4

        service = self.client['Account']
        service.getSubnets.return_value = [
            {
                'id': 100,
                'networkIdentifier': '10.0.0.1',
                'datacenter': {'name': 'dal00'},
                'version': 4,
            },
        ]

        result = self.network.list_subnets(
            identifier=identifier,
            datacenter=datacenter,
            version=version,
        )

        service.getSubnets.assert_called()

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
                'hardware': [],
                'networkComponents': [],
                'primaryRouter': {
                    'datacenter': {'name': 'dal00'}
                },
                'totalPrimaryIpAddressCount': 3,
                'subnets': [],
                'virtualGuests': []
            }
        ]

        expected = {'dal00': {
            'hardwareCount': 0,
            'networkingCount': 0,
            'primaryIpCount': 3,
            'subnetCount': 0,
            'virtualGuestCount': 0,
            'vlanCount': 1
        }}

        result = self.network.summary_by_datacenter()

        service.getNetworkVlans.assert_has_calls(mcall)
        self.assertEqual(expected, result)

    def test_resolve_ids_ip(self):
        service = self.client['Account']
        service.getSubnets.side_effect = [[
            {
                'id': '100',
                'networkIdentifier': '10.0.0.1',
                'datacenter': {'name': 'dal00'},
                'version': 4,
            },
        ], []]

        _id = self.network._get_subnet_by_identifier('10.0.0.1')
        self.assertEqual(_id, ['100'])

        _id = self.network._get_subnet_by_identifier('nope')
        self.assertEqual(_id, [])

    def _setup_add_subnet_mocks(self):
        package_mock = self.client['Product_Package']
        package_mock.getItems.return_value = [
            {
                'id': 4440,
                'capacity': '4',
                'description': '4 Portable Public IP Addresses',
                'itemCategory': {'categoryCode': 'sov_sec_ip_addresses_pub'},
                'prices': [{'id': 4444}],
            },
            {
                'id': 8880,
                'capacity': '8',
                'description': '8 Portable Public IP Addresses',
                'itemCategory': {'categoryCode': 'sov_sec_ip_addresses_pub'},
                'prices': [{'id': 8888}],
            },
            {
                'id': 44400,
                'capacity': '4',
                'description': '4 Portable Private IP Addresses',
                'itemCategory': {'categoryCode': 'sov_sec_ip_addresses_priv'},
                'prices': [{'id': 44441}],
            },
            {
                'id': 88800,
                'capacity': '8',
                'description': '8 Portable Private IP Addresses',
                'itemCategory': {'categoryCode': 'sov_sec_ip_addresses_priv'},
                'prices': [{'id': 88881}],
            },
            {
                'id': 10,
                'capacity': '0',
                'description': 'Global IPv4',
                'itemCategory': {'categoryCode': 'global_ipv4'},
                'prices': [{'id': 11}],
            },
            {
                'id': 66464,
                'capacity': '64',
                'description': '/64 Block Portable Public IPv6 Addresses',
                'itemCategory': {'categoryCode': 'static_ipv6_addresses'},
                'prices': [{'id': 664641}],
            },
            {
                'id': 610,
                'capacity': '0',
                'description': 'Global IPv6',
                'itemCategory': {'categoryCode': 'global_ipv6'},
                'prices': [{'id': 611}],
            },
        ]

        def vlan_return_mock(id, mask):
            return {'primaryRouter': {'datacenter': {'id': id * 10}}}

        vlan_mock = self.client['Network_Vlan']
        vlan_mock.getObject.side_effect = vlan_return_mock

        def order_return_mock(order):
            mock_item = {}
            for item in package_mock.getItems.return_value:
                if item['prices'][0]['id'] == order['prices'][0]['id']:
                    mock_item = item

            result = {
                'packageId': 0,
                'prices': [
                    {
                        'itemId': mock_item['id'],
                        'recurringFee': '0',
                        'id': mock_item['prices'][0]['id'],
                        'item': {
                            'capacity': mock_item['capacity'],
                            'description': mock_item['description'],
                            'id': mock_item['id']
                        },
                        'categories': [{
                            'categoryCode':
                            mock_item['itemCategory']['categoryCode']
                        }],
                    }
                ],
            }

            if order.get('location'):
                result['locationObject'] = {
                    'id': order['location'],
                    'name': 'test00',
                    'longName': 'Test Data Center'
                }
                result['location'] = order['location']

            return result

        order_mock = self.client['Product_Order']
        order_mock.verifyOrder.side_effect = order_return_mock
