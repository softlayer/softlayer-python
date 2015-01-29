"""
    SoftLayer.tests.managers.monitor_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import SoftLayer
from SoftLayer import testing


class MonitorTests(testing.TestCase):

    def set_up(self):
        self.hw_monitor_manager = SoftLayer.HardwareMonitorManager(self.client)
        self.vs_monitor_manager = SoftLayer.VSMonitorManager(self.client)

    def test_list_status(self):
        result = self.run_command(['monitor', 'status'])
        self.assertEqual(result.exit_code, 0)
        self.assert_called_with('SoftLayer_Account', 'getVirtualGuests')
        self.assert_called_with('SoftLayer_Account', 'getHardware')

    def test_list_only_hardware(self):
        result = self.run_command(['monitor', 'status', '--only_hardware'])
        self.assert_called_with('SoftLayer_Account', 'getHardware')
        self.assertEqual(result.exit_code, 0)

    def test_list_only_virtual(self):
        result = self.run_command(['monitor', 'status', '--only_virtual'])
        self.assert_called_with('SoftLayer_Account', 'getVirtualGuests')
        self.assertEqual(result.exit_code, 0)
