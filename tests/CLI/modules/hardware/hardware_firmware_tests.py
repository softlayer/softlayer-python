"""
    SoftLayer.tests.CLI.modules.hardware.hardware_firmware_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This suite is for the firmware related tests.

    :license: MIT, see LICENSE for more details.
"""
from SoftLayer.CLI import exceptions
from SoftLayer import testing
from unittest import mock as mock


class HardwareFirmwareTests(testing.TestCase):

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_update_firmware(self, confirm_mock):
        confirm_mock.return_value = True
        result = self.run_command(['server', 'update-firmware', '1000'])
        self.assert_no_fail(result)
        self.assertIn("Firmware update for 1000 started", result.output)
        self.assert_called_with('SoftLayer_Hardware_Server', 'createFirmwareUpdateTransaction',
                                args=((1, 1, 1, 1, 1)), identifier=1000)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_update_firmware_just_ipmi(self, confirm_mock):
        confirm_mock.return_value = True
        result = self.run_command(['server', 'update-firmware', '1000', '-i'])

        self.assert_no_fail(result)
        self.assertIn("Firmware update for 1000 started", result.output)
        self.assert_called_with('SoftLayer_Hardware_Server', 'createFirmwareUpdateTransaction',
                                args=((1, 0, 0, 0, 0)), identifier=1000)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_update_firmware_just_raid(self, confirm_mock):
        confirm_mock.return_value = True
        result = self.run_command(['server', 'update-firmware', '1000', '-r'])

        self.assert_no_fail(result)
        self.assertIn("Firmware update for 1000 started", result.output)
        self.assert_called_with('SoftLayer_Hardware_Server', 'createFirmwareUpdateTransaction',
                                args=((0, 1, 0, 0, 0)), identifier=1000)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_update_firmware_just_bios(self, confirm_mock):
        confirm_mock.return_value = True
        result = self.run_command(['server', 'update-firmware', '1000', '-b'])

        self.assert_no_fail(result)
        self.assertIn("Firmware update for 1000 started", result.output)
        self.assert_called_with('SoftLayer_Hardware_Server', 'createFirmwareUpdateTransaction',
                                args=((0, 0, 1, 0, 0)), identifier=1000)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_update_firmware_just_disk(self, confirm_mock):
        confirm_mock.return_value = True
        result = self.run_command(['server', 'update-firmware', '1000', '-d'])

        self.assert_no_fail(result)
        self.assertIn("Firmware update for 1000 started", result.output)
        self.assert_called_with('SoftLayer_Hardware_Server', 'createFirmwareUpdateTransaction',
                                args=((0, 0, 0, 1, 0)), identifier=1000)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_update_firmware_just_nic(self, confirm_mock):
        confirm_mock.return_value = True
        result = self.run_command(['server', 'update-firmware', '1000', '-n'])

        self.assert_no_fail(result)
        self.assertIn("Firmware update for 1000 started", result.output)
        self.assert_called_with('SoftLayer_Hardware_Server', 'createFirmwareUpdateTransaction',
                                args=((0, 0, 0, 0, 1)), identifier=1000)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_update_firmware_just_all(self, confirm_mock):
        confirm_mock.return_value = True
        result = self.run_command(['server', 'update-firmware', '1000', '-i', '-r', '-b', '-d', '-n'])

        self.assert_no_fail(result)
        self.assertIn("Firmware update for 1000 started", result.output)
        self.assert_called_with('SoftLayer_Hardware_Server', 'createFirmwareUpdateTransaction',
                                args=((1, 1, 1, 1, 1)), identifier=1000)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_update_firmware_no_confirm(self, confirm_mock):
        confirm_mock.return_value = False

        result = self.run_command(['server', 'update-firmware', '1000'])
        self.assertEqual(result.exit_code, 2)
        self.assertIsInstance(result.exception, exceptions.CLIAbort)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_reflash_firmware(self, confirm_mock):
        confirm_mock.return_value = True
        result = self.run_command(['server', 'reflash-firmware', '1000'])

        self.assert_no_fail(result)
        self.assertEqual(result.output, 'Successfully device firmware reflashed\n')
        self.assert_called_with('SoftLayer_Hardware_Server', 'createFirmwareReflashTransaction',
                                args=((1, 1, 1)), identifier=1000)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_reflash_firmware_no_confirm(self, confirm_mock):
        confirm_mock.return_value = False

        result = self.run_command(['server', 'reflash-firmware', '1000'])
        self.assertEqual(result.exit_code, 2)
        self.assertIsInstance(result.exception, exceptions.CLIAbort)
