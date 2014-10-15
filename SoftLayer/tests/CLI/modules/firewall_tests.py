"""
    SoftLayer.tests.CLI.modules.firewall_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import json

from SoftLayer import testing


class FirewallTests(testing.TestCase):
    def set_up(self):
        self.client = testing.FixtureClient()

    def test_list_firewalls(self):
        result = testing.run_command(['firewall', 'list'])

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(json.loads(result.output),
                         [{'type': 'VLAN - dedicated',
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
                           'type': 'Server - standard'}])
