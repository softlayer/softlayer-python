"""
    SoftLayer.tests.managers.monitor_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import mock

import SoftLayer
from SoftLayer import testing
from SoftLayer.testing import fixtures


class MonitorTests(testing.TestCase):

    def set_up(self):
        self.client = testing.FixtureClient()
        self.monitor_manager = SoftLayer.MonitoringManager(self.client)

    def test_list_hardware_status(self):
        mcall = mock.call(mask=mock.ANY, filter='')
        service = self.client['Account']

        result = self.monitor_manager.list_hardware_status()
        self.assertEqual(result, fixtures.Account.getHardware)
        service.getHardware.assert_has_calls(mcall)

    def test_list_guest_status(self):
        mcall = mock.call(mask=mock.ANY, filter='')
        service = self.client['Account']

        result = self.monitor_manager.list_guest_status()
        self.assertEqual(result, fixtures.Account.getVirtualGuests)
        service.getVirtualGuests.assert_has_calls(mcall)