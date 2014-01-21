"""
    SoftLayer.tests.managers.firewall_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
from SoftLayer import FirewallManager
from SoftLayer.tests import unittest, FixtureClient
from SoftLayer.tests.fixtures import Account

from mock import ANY


class FirewallTests(unittest.TestCase):

    def setUp(self):
        self.client = FixtureClient()
        self.firewall = FirewallManager(self.client)

    def test_get_firewalls(self):
        call = self.client['Account'].getObject

        firewalls = self.firewall.get_firewalls()

        call.assert_called_once_with(mask=ANY)
        self.assertEqual(firewalls, Account.getObject['networkVlans'])
