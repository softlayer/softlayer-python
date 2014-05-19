"""
    SoftLayer.tests.CLI.modules.firewall_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
# from mock import patch

from SoftLayer.tests import unittest, FixtureClient
from SoftLayer.CLI.helpers import format_output
# from SoftLayer.CLI.exceptions import CLIAbort
from SoftLayer.CLI.modules import firewall


class FirewallTests(unittest.TestCase):
    def setUp(self):
        self.client = FixtureClient()

    def test_list_firewalls(self):
        call = self.client['Account'].getNetworkVlans
        call.return_value = [{
            'id': 1,
            'dedicatedFirewallFlag': True,
            'highAvailabilityFirewallFlag': True,
            'networkVlanFirewall': {'id': 1234},
        }, {
            'id': 2,
            'dedicatedFirewallFlag': False,
            'firewallGuestNetworkComponents': [{
                'id': 1234,
                'guestNetworkComponent': {'guest': {'id': 1}},
                'status': 'ok'}],
            'firewallNetworkComponents': [{
                'id': 1234,
                'networkComponent': {'downlinkComponent': {'hardwareId': 1}},
                'status': 'ok'}],
        }
        ]
        command = firewall.FWList(client=self.client)

        output = command.execute({})

        self.assertEqual([{'type': 'VLAN - dedicated',
                           'server/vlan id': 1,
                           'features': ['HA'],
                           'firewall id': 'vlan:1234'},
                          {'features': '-',
                           'firewall id': 'cci:1234',
                           'server/vlan id': 1,
                           'type': 'CCI - standard'},
                          {'features': '-',
                           'firewall id': 'server:1234',
                           'server/vlan id': 1,
                           'type': 'Server - standard'}],
                         format_output(output, 'python'))
