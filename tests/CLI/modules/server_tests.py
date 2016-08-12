"""
    SoftLayer.tests.CLI.modules.server_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This is a series of integration tests designed to test the complete
    command line interface.

    :license: MIT, see LICENSE for more details.
"""

import mock

from SoftLayer.CLI import exceptions
from SoftLayer import testing

import json
import tempfile


class ServerCLITests(testing.TestCase):

    def test_server_cancel_reasons(self):
        result = self.run_command(['server', 'cancel-reasons'])
        output = json.loads(result.output)
        self.assert_no_fail(result)
        self.assertEqual(len(output), 10)

    def test_server_details(self):
        result = self.run_command(['server', 'detail', '1234',
                                   '--passwords', '--price'])
        expected = {
            'cores': 2,
            'created': '2013-08-01 15:23:45',
            'datacenter': 'TEST00',
            'guid': '1a2b3c-1701',
            'domain': 'test.sftlyr.ws',
            'hostname': 'hardware-test1',
            'fqdn': 'hardware-test1.test.sftlyr.ws',
            'id': 1000,
            'ipmi_ip': '10.1.0.3',
            'memory': 2048,
            'notes': 'These are test notes.',
            'os': 'Ubuntu',
            'owner': 'chechu',
            'price rate': 16.08,
            'private_ip': '10.1.0.2',
            'ptr': '2.0.1.10.in-addr.arpa',
            'public_ip': '172.16.1.100',
            'remote users': [{'password': 'abc123', 'ipmi_username': 'root'}],
            'status': 'ACTIVE',
            'tags': ['test_tag'],
            'users': [{'password': 'abc123', 'username': 'root'}],
            'vlans': [{'id': 9653, 'number': 1800, 'type': 'PRIVATE'},
                      {'id': 19082, 'number': 3672, 'type': 'PUBLIC'}]
        }

        self.assert_no_fail(result)
        self.assertEqual(json.loads(result.output), expected)

    def test_detail_vs_empty_tag(self):
        mock = self.set_mock('SoftLayer_Hardware_Server', 'getObject')
        mock.return_value = {
            'id': 100,
            'processorPhysicalCoreAmount': 2,
            'memoryCapacity': 2,
            'tagReferences': [
                {'tag': {'name': 'example-tag'}},
                {},
            ],
        }
        result = self.run_command(['server', 'detail', '100'])

        self.assert_no_fail(result)
        self.assertEqual(
            json.loads(result.output)['tags'],
            ['example-tag'],
        )

    def test_list_servers(self):
        result = self.run_command(['server', 'list', '--tag=openstack'])

        expected = [
            {
                'datacenter': 'TEST00',
                'primary_ip': '172.16.1.100',
                'hostname': 'hardware-test1',
                'id': 1000,
                'backend_ip': '10.1.0.2',
                'action': 'TXN_NAME',
            },
            {
                'datacenter': 'TEST00',
                'primary_ip': '172.16.4.94',
                'hostname': 'hardware-test2',
                'id': 1001,
                'backend_ip': '10.1.0.3',
                'action': None,
            },
            {
                'datacenter': 'TEST00',
                'primary_ip': '172.16.4.95',
                'hostname': 'hardware-bad-memory',
                'id': 1002,
                'backend_ip': '10.1.0.4',
                'action': None,
            },
            {
                'action': None,
                'backend_ip': None,
                'datacenter': None,
                'hostname': None,
                'id': 1003,
                'primary_ip': None,
            },
        ]

        self.assert_no_fail(result)
        self.assertEqual(expected, json.loads(result.output))

    @mock.patch('SoftLayer.CLI.formatting.no_going_back')
    @mock.patch('SoftLayer.HardwareManager.reload')
    def test_server_reload(self, reload_mock, ngb_mock):
        ngb_mock.return_value = False

        # Check the positive case
        result = self.run_command(['--really', 'server', 'reload', '12345',
                                   '--key=4567'])

        self.assert_no_fail(result)
        reload_mock.assert_called_with(12345, None, [4567])

        # Now check to make sure we properly call CLIAbort in the negative case
        result = self.run_command(['server', 'reload', '12345'])

        self.assertEqual(result.exit_code, 2)
        self.assertIsInstance(result.exception, exceptions.CLIAbort)

    @mock.patch('SoftLayer.CLI.formatting.no_going_back')
    @mock.patch('SoftLayer.HardwareManager.cancel_hardware')
    def test_cancel_server(self, cancel_mock, ngb_mock):
        ngb_mock.return_value = False

        # Check the positive case
        result = self.run_command(['--really', 'server', 'cancel', '12345',
                                   '--reason=Test', '--comment=Test'])

        self.assert_no_fail(result)
        cancel_mock.assert_called_with(12345, "Test", "Test", False)

        # Test
        result = self.run_command(['server', 'cancel', '12345',
                                   '--reason=Test', '--comment=Test'])

        self.assertEqual(result.exit_code, 2)
        self.assertIsInstance(result.exception, exceptions.CLIAbort)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_server_power_off(self, confirm_mock):
        # Check the positive case
        result = self.run_command(['--really', 'server', 'power-off', '12345'])

        self.assert_called_with('SoftLayer_Hardware_Server', 'powerOff',
                                identifier=12345)

        # Now check to make sure we properly call CLIAbort in the negative case
        confirm_mock.return_value = False
        result = self.run_command(['server', 'power-off', '12345'])

        self.assertEqual(result.exit_code, 2)
        self.assertIsInstance(result.exception, exceptions.CLIAbort)

    def test_server_reboot_default(self):
        result = self.run_command(['--really', 'server', 'reboot', '12345'])

        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Hardware_Server', 'rebootDefault',
                                identifier=12345)

    def test_server_reboot_soft(self):
        result = self.run_command(['--really', 'server', 'reboot', '12345',
                                   '--soft'])

        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Hardware_Server', 'rebootSoft',
                                identifier=12345)

    def test_server_reboot_hard(self):
        result = self.run_command(['--really', 'server', 'reboot', '12345',
                                   '--hard'])

        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Hardware_Server', 'rebootHard',
                                identifier=12345)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_server_reboot_negative(self, confirm_mock):
        confirm_mock.return_value = False
        result = self.run_command(['server', 'reboot', '12345'])

        self.assertEqual(result.exit_code, 2)
        self.assertIsInstance(result.exception, exceptions.CLIAbort)

    def test_server_power_on(self):
        result = self.run_command(['--really', 'server', 'power-on', '12345'])

        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Hardware_Server', 'powerOn',
                                identifier=12345)

    def test_server_power_cycle(self):
        result = self.run_command(['--really', 'server', 'power-cycle',
                                   '12345'])

        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Hardware_Server', 'powerCycle',
                                identifier=12345)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_server_power_cycle_negative(self, confirm_mock):
        confirm_mock.return_value = False
        result = self.run_command(['server', 'power-cycle', '12345'])

        self.assertEqual(result.exit_code, 2)
        self.assertIsInstance(result.exception, exceptions.CLIAbort)

    @mock.patch('SoftLayer.HardwareManager.verify_order')
    def test_create_server_test_flag(self, verify_mock):
        verify_mock.return_value = {
            'prices': [
                {
                    'recurringFee': 0.0,
                    'setupFee': 0.0,
                    'item': {'description': 'First Item'},
                },
                {
                    'recurringFee': 25.0,
                    'setupFee': 0.0,
                    'item': {'description': 'Second Item'},
                }
            ]
        }

        result = self.run_command(['--really', 'server', 'create',
                                   '--size=S1270_8GB_2X1TBSATA_NORAID',
                                   '--hostname=test',
                                   '--domain=example.com',
                                   '--datacenter=TEST00',
                                   '--port-speed=100',
                                   '--os=UBUNTU_12_64',
                                   '--test'],
                                  fmt='raw')

        self.assert_no_fail(result)
        self.assertIn("First Item", result.output)
        self.assertIn("Second Item", result.output)
        self.assertIn("Total monthly cost", result.output)

    def test_create_options(self):
        result = self.run_command(['server', 'create-options'])

        self.assert_no_fail(result)
        expected = [
            [{'datacenter': 'Washington 1', 'value': 'wdc01'}],
            [{'size': 'Single Xeon 1270, 8GB Ram, 2x1TB SATA disks, Non-RAID',
              'value': 'S1270_8GB_2X1TBSATA_NORAID'}],
            [{'operating_system': 'Ubuntu / 14.04-64',
              'value': 'UBUNTU_14_64'}],
            [{'port_speed': '10 Mbps Public & Private Network Uplinks',
              'value': '10'}],
            [{'extras': '1 IPv6 Address', 'value': '1_IPV6_ADDRESS'}]]
        self.assertEqual(json.loads(result.output), expected)

    @mock.patch('SoftLayer.HardwareManager.place_order')
    def test_create_server(self, order_mock):
        order_mock.return_value = {
            'orderId': 98765,
            'orderDate': '2013-08-02 15:23:47'
        }

        result = self.run_command(['--really', 'server', 'create',
                                   '--size=S1270_8GB_2X1TBSATA_NORAID',
                                   '--hostname=test',
                                   '--domain=example.com',
                                   '--datacenter=TEST00',
                                   '--port-speed=100',
                                   '--os=UBUNTU_12_64',
                                   '--no-public',
                                   '--key=10',
                                   ])

        self.assert_no_fail(result)
        self.assertEqual(json.loads(result.output),
                         {'id': 98765, 'created': '2013-08-02 15:23:47'})

    def test_create_server_missing_required(self):

        # This is missing a required argument
        result = self.run_command(['server', 'create',
                                   # Note: no chassis id
                                   '--hostname=test',
                                   '--domain=example.com',
                                   '--datacenter=TEST00',
                                   '--network=100',
                                   '--os=UBUNTU_12_64_MINIMAL',
                                   ])

        self.assertEqual(result.exit_code, 2)
        self.assertIsInstance(result.exception, SystemExit)

    @mock.patch('SoftLayer.CLI.template.export_to_template')
    def test_create_server_with_export(self, export_mock):
        result = self.run_command(['--really', 'server', 'create',
                                   '--size=S1270_8GB_2X1TBSATA_NORAID',
                                   '--hostname=test',
                                   '--domain=example.com',
                                   '--datacenter=TEST00',
                                   '--port-speed=100',
                                   '--os=UBUNTU_12_64',
                                   '--no-public',
                                   '--export=/path/to/test_file.txt'],
                                  fmt='raw')

        self.assert_no_fail(result)
        self.assertIn("Successfully exported options to a template file.",
                      result.output)
        export_mock.assert_called_with('/path/to/test_file.txt',
                                       {'billing': 'hourly',
                                        'datacenter': 'TEST00',
                                        'domain': 'example.com',
                                        'extra': (),
                                        'hostname': 'test',
                                        'key': (),
                                        'os': 'UBUNTU_12_64',
                                        'port_speed': 100,
                                        'postinstall': None,
                                        'size': 'S1270_8GB_2X1TBSATA_NORAID',
                                        'test': False,
                                        'no_public': True,
                                        'wait': None,
                                        'template': None},
                                       exclude=['wait', 'test'])

    def test_edit_server_userdata_and_file(self):
        # Test both userdata and userfile at once
        with tempfile.NamedTemporaryFile() as userfile:
            result = self.run_command(['server', 'edit', '1000',
                                       '--hostname=hardware-test1',
                                       '--domain=test.sftlyr.ws',
                                       '--userdata=My data',
                                       '--userfile=%s' % userfile.name])

            self.assertEqual(result.exit_code, 2)
            self.assertIsInstance(result.exception, exceptions.ArgumentError)

    def test_edit_server_userdata(self):
        result = self.run_command(['server', 'edit', '1000',
                                   '--hostname=hardware-test1',
                                   '--domain=test.sftlyr.ws',
                                   '--userdata=My data'])

        self.assert_no_fail(result)
        self.assertEqual(result.output, "")
        self.assert_called_with('SoftLayer_Hardware_Server', 'editObject',
                                args=({'domain': 'test.sftlyr.ws',
                                       'hostname': 'hardware-test1'},),
                                identifier=1000)

    @mock.patch('SoftLayer.HardwareManager.edit')
    def test_edit_server_failed(self, edit_mock):
        edit_mock.return_value = False
        result = self.run_command(['server', 'edit', '1000',
                                   '--hostname=hardware-test1',
                                   '--domain=test.sftlyr.ws',
                                   '--userdata=My data'])

        self.assertEqual(result.exit_code, 2)
        self.assertEqual(result.output, "")
        edit_mock.assert_called_with(1000,
                                     userdata='My data',
                                     domain='test.sftlyr.ws',
                                     hostname='hardware-test1')

    def test_edit_server_userfile(self):
        with tempfile.NamedTemporaryFile() as userfile:
            userfile.write(b"some data")
            userfile.flush()

            result = self.run_command(['server', 'edit', '1000',
                                       '--userfile=%s' % userfile.name])

            self.assert_no_fail(result)
            self.assertEqual(result.output, "")
            self.assert_called_with('SoftLayer_Hardware_Server',
                                    'setUserMetadata',
                                    args=(['some data'],),
                                    identifier=1000)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_update_firmware(self, confirm_mock):
        confirm_mock.return_value = True
        result = self.run_command(['server', 'update-firmware', '1000'])

        self.assert_no_fail(result)
        self.assertEqual(result.output, "")
        self.assert_called_with('SoftLayer_Hardware_Server',
                                'createFirmwareUpdateTransaction',
                                args=((1, 1, 1, 1)), identifier=1000)

    def test_edit(self):
        result = self.run_command(['server', 'edit',
                                   '--domain=example.com',
                                   '--hostname=host',
                                   '--userdata="testdata"',
                                   '--tag=dev',
                                   '--tag=green',
                                   '--public-speed=10',
                                   '--private-speed=100',
                                   '100'])

        self.assert_no_fail(result)
        self.assertEqual(result.output, '')

        self.assert_called_with(
            'SoftLayer_Hardware_Server', 'editObject',
            args=({'domain': 'example.com', 'hostname': 'host'},),
            identifier=100,
        )
        self.assert_called_with(
            'SoftLayer_Hardware_Server', 'setUserMetadata',
            args=(['"testdata"'],),
            identifier=100,
        )
        self.assert_called_with(
            'SoftLayer_Hardware_Server', 'setPublicNetworkInterfaceSpeed',
            args=(10,),
            identifier=100,
        )
        self.assert_called_with(
            'SoftLayer_Hardware_Server', 'setPrivateNetworkInterfaceSpeed',
            args=(100,),
            identifier=100,
        )
