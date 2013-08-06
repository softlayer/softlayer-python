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
            {
                'id': 101,
                'networkIdentifier': '10.0.1.1',
                'datacenter': {'name': 'dal05'},
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
        service.getSubnets.return_value = [
            {
                'id': '100',
                'networkIdentifier': '10.0.0.1',
                'datacenter': {'name': 'dal00'},
                'version': 4,
            },
            {
                'id': '101',
                'networkIdentifier': '10.0.1.1',
                'datacenter': {'name': 'dal05'},
                'version': 4,
            },
        ]

        _id = self.network._get_subnet_by_identifier('10.0.0.1')
        self.assertEqual(_id, ['100'])

        _id = self.network._get_subnet_by_identifier('nope')
        self.assertEqual(_id, [])
