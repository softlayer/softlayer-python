"""
    SoftLayer.tests.CLI.modules.firewall_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import json

from SoftLayer import testing


class FirewallTests(testing.TestCase):

    def test_list_firewalls(self):
        result = self.run_command(['firewall', 'list'])

        self.assert_no_fail(result)
        self.assertEqual(json.loads(result.output),
                         [{'type': 'VLAN - dedicated',
                           'server/vlan id': 1,
                           'features': ['HA'],
                           'firewall id': 'vlan:1234'},
                          {'features': '-',
                           'firewall id': 'vs:1234',
                           'server/vlan id': 1,
                           'type': 'Virtual Server - standard'},
                          {'features': '-',
                           'firewall id': 'server:1234',
                           'server/vlan id': 1,
                           'type': 'Server - standard'}])
