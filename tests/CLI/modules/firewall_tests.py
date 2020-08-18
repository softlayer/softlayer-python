"""
    SoftLayer.tests.CLI.modules.firewall_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import json
from unittest import mock

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
