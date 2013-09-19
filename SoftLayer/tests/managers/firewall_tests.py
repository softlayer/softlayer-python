"""
    SoftLayer.tests.managers.firewall_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
    :license: MIT, see LICENSE for more details.
"""
from SoftLayer import FirewallManager
from SoftLayer.tests import unittest

from mock import MagicMock, ANY


class FirewallTests(unittest.TestCase):

    def setUp(self):
        self.client = MagicMock()
        self.firewall = FirewallManager(self.client)

    def test_get_firewalls(self):
        vlan = {
            'dedicatedFirewallFlag': True,
        }
        call = self.client['Account'].getObject
        call.return_value = {'networkVlans': [vlan]}

        firewalls = self.firewall.get_firewalls()

        self.assertEqual([vlan], firewalls)
        call.assert_called_once_with(mask=ANY)
