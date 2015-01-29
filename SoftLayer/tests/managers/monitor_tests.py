"""
    SoftLayer.tests.managers.monitor_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import SoftLayer
from SoftLayer import testing
from SoftLayer.testing import fixtures


class MonitorTests(testing.TestCase):

    def set_up(self):
        self.hw_monitor_manager = SoftLayer.HardwareMonitorManager(self.client)
        self.vs_monitor_manager = SoftLayer.VSMonitorManager(self.client)

    def test_list_hardware_status(self):
        result = self.hw_monitor_manager.list_status()
        self.assertEqual(result, fixtures.SoftLayer_Account.getHardware)
        self.assert_called_with('SoftLayer_Account', 'getHardware')

    def test_list_guest_status(self):
        result = self.vs_monitor_manager.list_status()
        self.assertEqual(result, fixtures.SoftLayer_Account.getVirtualGuests)
        self.assert_called_with('SoftLayer_Account', 'getVirtualGuests')
