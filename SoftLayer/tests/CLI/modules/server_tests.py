"""
    SoftLayer.tests.CLI.modules.server_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This is a series of integration tests designed to test the complete
    command line interface.

    :license: MIT, see LICENSE for more details.
"""

import mock

from SoftLayer.CLI import exceptions
from SoftLayer.CLI.server import create
from SoftLayer import testing

import json
import tempfile


class ServerCLITests(testing.TestCase):

    def test_server_cancel_reasons(self):
        result = self.run_command(['server', 'cancel-reasons'])
        output = json.loads(result.output)
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(len(output), 10)

    @mock.patch('SoftLayer.HardwareManager'
                '.get_available_dedicated_server_packages')
    def test_server_create_options(self, packages):

        packages.return_value = [(999, 'Chassis 999')]

        result = self.run_command(['server', 'create-options', '999'])

        expected = {
            'cpu': [
                {'Description': 'Dual Quad Core Pancake 200 - 1.60GHz',
                 'ID': 723},
                {'Description': 'Dual Quad Core Pancake 200 - 1.80GHz',
                 'ID': 724}],
            'datacenter': ['RANDOM_LOCATION'],
            'disk': ['250_SATA_II', '500_SATA_II'],
            'disk_controllers': ['None', 'RAID0'],
            'dual nic': ['1000_DUAL', '100_DUAL', '10_DUAL'],
            'memory': [4, 6],
            'os (CENTOS)': ['CENTOS_6_64_LAMP', 'CENTOS_6_64_MINIMAL'],
            'os (REDHAT)': ['REDHAT_6_64_LAMP', 'REDHAT_6_64_MINIMAL'],
            'os (UBUNTU)': ['UBUNTU_12_64_LAMP', 'UBUNTU_12_64_MINIMAL'],
            'os (WIN)': [
                'WIN_2008-DC_64',
                'WIN_2008-ENT_64',
                'WIN_2008-STD-R2_64',
                'WIN_2008-STD_64',
                'WIN_2012-DC-HYPERV_64'],
            'single nic': ['100', '1000']}

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(json.loads(result.output), expected)

    @mock.patch('SoftLayer.HardwareManager'
                '.get_available_dedicated_server_packages')
    def test_server_create_options_with_invalid_chassis(self, packages):
        packages.return_value = [(998, 'Legacy Chassis')]
        result = self.run_command(['server', 'create-options', '999'])

        self.assertEqual(result.exit_code, 2)
        self.assertIsInstance(result.exception, exceptions.CLIAbort)

    @mock.patch('SoftLayer.HardwareManager'
                '.get_available_dedicated_server_packages')
    @mock.patch('SoftLayer.HardwareManager.get_bare_metal_package_id')
    def test_server_create_options_for_bmc(self, bmpi, packages):
        packages.return_value = [(1099, 'Bare Metal Instance')]
        bmpi.return_value = '1099'

        result = self.run_command(['server', 'create-options', '1099'])

        expected = {
            'memory/cpu': [
                {'cpu': ['2'], 'memory': '2'},
                {'cpu': ['2', '4'], 'memory': '4'},
            ],
            'datacenter': ['RANDOM_LOCATION'],
            'disk': ['250_SATA_II', '500_SATA_II'],
            'dual nic': ['1000_DUAL', '100_DUAL', '10_DUAL'],
            'os (CENTOS)': ['CENTOS_6_64_LAMP', 'CENTOS_6_64_MINIMAL'],
            'os (REDHAT)': ['REDHAT_6_64_LAMP', 'REDHAT_6_64_MINIMAL'],
            'os (UBUNTU)': ['UBUNTU_12_64_LAMP', 'UBUNTU_12_64_MINIMAL'],
            'os (WIN)': [
                'WIN_2008-DC_64',
                'WIN_2008-ENT_64',
                'WIN_2008-STD-R2_64',
                'WIN_2008-STD_64',
                'WIN_2012-DC-HYPERV_64'],
            'single nic': ['100', '1000']}

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(json.loads(result.output), expected)

    def test_server_details(self):
        result = self.run_command(['server', 'detail', '1234',
                                   '--passwords', '--price'])

        expected = {
            'status': 'ACTIVE',
            'datacenter': 'TEST00',
            'created': '2013-08-01 15:23:45',
            'notes': 'These are test notes.',
            'hostname': 'hardware-test1.test.sftlyr.ws',
            'public_ip': '172.16.1.100',
            'private_ip': '10.1.0.2',
            'ipmi_ip': '10.1.0.3',
            'price rate': 1.54,
            'memory': 2048,
            'cores': 2,
            'ptr': '2.0.1.10.in-addr.arpa',
            'os': 'Ubuntu',
            'id': 1000,
            'tags': ['test_tag'],
            'users': ['root abc123'],
            'vlans': [{'id': 9653, 'number': 1800, 'type': 'PRIVATE'},
                      {'id': 19082, 'number': 3672, 'type': 'PUBLIC'}],
            'owner': 'chechu'
        }

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(json.loads(result.output), expected)

    def test_list_servers(self):
        result = self.run_command(['server', 'list', '--tag=openstack'])

        expected = [
            {
                'datacenter': 'TEST00',
                'primary_ip': '172.16.1.100',
                'host': 'hardware-test1',
                'globalIdentifier': 1000,
                'backend_ip': '10.1.0.2',
                'action': 'TXN_NAME',
            },
            {
                'datacenter': 'TEST00',
                'primary_ip': '172.16.4.94',
                'host': 'hardware-test2',
                'globalIdentifier': 1001,
                'backend_ip': '10.1.0.3',
                'action': None,
            },
            {
                'datacenter': 'TEST00',
                'primary_ip': '172.16.4.95',
                'host': 'hardware-bad-memory',
                'globalIdentifier': 1002,
                'backend_ip': '10.1.0.4',
                'action': None,
            }
        ]

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(json.loads(result.output), expected)

    @mock.patch('SoftLayer.CLI.formatting.no_going_back')
    @mock.patch('SoftLayer.HardwareManager.reload')
    def test_server_reload(self, reload_mock, ngb_mock):
        ngb_mock.return_value = False

        # Check the positive case
        result = self.run_command(['--really', 'server', 'reload', '12345',
                                   '--key=4567'])

        self.assertEqual(result.exit_code, 0)
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

        self.assertEqual(result.exit_code, 0)
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

        self.assertEqual(result.exit_code, 0)
        self.assert_called_with('SoftLayer_Hardware_Server', 'rebootDefault',
                                identifier=12345)

    def test_server_reboot_soft(self):
        result = self.run_command(['--really', 'server', 'reboot', '12345',
                                   '--soft'])

        self.assertEqual(result.exit_code, 0)
        self.assert_called_with('SoftLayer_Hardware_Server', 'rebootSoft',
                                identifier=12345)

    def test_server_reboot_hard(self):
        result = self.run_command(['--really', 'server', 'reboot', '12345',
                                   '--hard'])

        self.assertEqual(result.exit_code, 0)
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

        self.assertEqual(result.exit_code, 0)
        self.assert_called_with('SoftLayer_Hardware_Server', 'powerOn',
                                identifier=12345)

    def test_server_power_cycle(self):
        result = self.run_command(['--really', 'server', 'power-cycle',
                                   '12345'])

        self.assertEqual(result.exit_code, 0)
        self.assert_called_with('SoftLayer_Hardware_Server', 'powerCycle',
                                identifier=12345)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_server_power_cycle_negative(self, confirm_mock):
        confirm_mock.return_value = False
        result = self.run_command(['server', 'power-cycle', '12345'])

        self.assertEqual(result.exit_code, 2)
        self.assertIsInstance(result.exception, exceptions.CLIAbort)

    def test_nic_edit_server(self):
        result = self.run_command(['server', 'nic-edit', '12345', 'public',
                                   '--speed=100'])

        self.assertEqual(result.exit_code, 0)
        self.assert_called_with('SoftLayer_Hardware_Server',
                                'setPublicNetworkInterfaceSpeed',
                                args=(100,),
                                identifier=12345)

    @mock.patch('SoftLayer.HardwareManager'
                '.get_available_dedicated_server_packages')
    def test_list_chassis_server(self, packages):
        packages.return_value = [(1, 'Chassis 1', 'Some chassis'),
                                 (2, 'Chassis 2', 'Another chassis')]
        result = self.run_command(['server', 'list-chassis'])

        expected = [{'chassis': 'Chassis 1', 'code': 1},
                    {'chassis': 'Chassis 2', 'code': 2}]

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(json.loads(result.output), expected)

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
        result = self.run_command(['server', 'create',
                                   '--chassis=999',
                                   '--hostname=test',
                                   '--domain=example.com',
                                   '--datacenter=TEST00',
                                   '--cpu=4',
                                   '--network=100',
                                   '--disk=250_SATA_II',
                                   '--disk=250_SATA_II',
                                   '--os=UBUNTU_12_64_MINIMAL',
                                   '--memory=4',
                                   '--controller=RAID0',
                                   '--test',
                                   '--key=1234',
                                   '--key=456',
                                   '--vlan-public=10234',
                                   '--vlan-private=20468',
                                   '--postinstall='
                                   'http://somescript.foo/myscript.sh',
                                   ],
                                  fmt='raw')

        self.assertEqual(result.exit_code, 0)
        self.assertIn("First Item", result.output)
        self.assertIn("Second Item", result.output)
        self.assertIn("Total monthly cost", result.output)

    @mock.patch('SoftLayer.HardwareManager.verify_order')
    def test_create_server_test_no_disk(self, verify_mock):

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
        result = self.run_command(['server', 'create',
                                   '--chassis=999',
                                   '--hostname=test',
                                   '--domain=example.com',
                                   '--datacenter=TEST00',
                                   '--cpu=4',
                                   '--network=100',
                                   '--os=UBUNTU_12_64_MINIMAL',
                                   '--memory=4',
                                   '--controller=RAID0',
                                   '--test',
                                   '--key=1234',
                                   '--key=456',
                                   '--vlan-public=10234',
                                   '--vlan-private=20468',
                                   '--postinstall='
                                   'http://somescript.foo/myscript.sh',
                                   ],
                                  fmt='raw')

        self.assertEqual(result.exit_code, 0)

    @mock.patch('SoftLayer.HardwareManager.verify_order')
    def test_create_server_test_no_disk_no_raid(self, verify_mock):
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

        result = self.run_command(['server', 'create',
                                   '--chassis=999',
                                   '--hostname=test',
                                   '--domain=example.com',
                                   '--datacenter=TEST00',
                                   '--cpu=4',
                                   '--network=100',
                                   '--os=UBUNTU_12_64_MINIMAL',
                                   '--memory=4',
                                   '--test',
                                   '--vlan-public=10234',
                                   '--vlan-private=20468',
                                   ],
                                  fmt='raw')

        self.assertEqual(result.exit_code, 0)

    @mock.patch('SoftLayer.HardwareManager.place_order')
    def test_create_server(self, order_mock):
        order_mock.return_value = {
            'orderId': 98765,
            'orderDate': '2013-08-02 15:23:47'
        }

        result = self.run_command(['--really', 'server', 'create',
                                   '--chassis=999',
                                   '--hostname=test',
                                   '--domain=example.com',
                                   '--datacenter=TEST00',
                                   '--cpu=4',
                                   '--network=100',
                                   '--os=UBUNTU_12_64_MINIMAL',
                                   '--memory=4',
                                   '--vlan-public=10234',
                                   '--vlan-private=20468',
                                   ])

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(json.loads(result.output),
                         {'id': 98765, 'created': '2013-08-02 15:23:47'})

    def test_create_server_missing_required(self):

        # This is missing a required argument
        result = self.run_command(['server', 'create',
                                   # Note: no chassis id
                                   '--hostname=test',
                                   '--domain=example.com',
                                   '--datacenter=TEST00',
                                   '--cpu=4',
                                   '--network=100',
                                   '--os=UBUNTU_12_64_MINIMAL',
                                   '--memory=4',
                                   ])

        self.assertEqual(result.exit_code, 1)
        self.assertIsInstance(result.exception, SystemExit)

    @mock.patch('SoftLayer.CLI.template.export_to_template')
    def test_create_server_with_export(self, export_to_template):
        result = self.run_command(['server', 'create',
                                   # Note: no chassis id
                                   '--chassis=999',
                                   '--hostname=test',
                                   '--domain=example.com',
                                   '--datacenter=TEST00',
                                   '--cpu=4',
                                   '--memory=4',
                                   '--network=100',
                                   '--os=UBUNTU_12_64_MINIMAL',
                                   '--key=1234',
                                   '--export=/path/to/test_file.txt',
                                   ])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("Successfully exported options to a template file.",
                      result.output)
        export_to_template.assert_called_with('/path/to/test_file.txt',
                                              {'domain': 'example.com',
                                               'san': False,
                                               'dedicated': False,
                                               'private': False,
                                               'disk': (),
                                               'userdata': None,
                                               'network': '100',
                                               'billing': 'monthly',
                                               'userfile': None,
                                               'hostname': 'test',
                                               'template': None,
                                               'memory': 4,
                                               'test': False,
                                               'postinstall': None,
                                               'controller': None,
                                               'chassis': '999',
                                               'key': ('1234',),
                                               'vlan_private': None,
                                               'wait': None,
                                               'datacenter': 'TEST00',
                                               'os': 'UBUNTU_12_64_MINIMAL',
                                               'cpu': 4,
                                               'vlan_public': None},
                                              exclude=['wait', 'test'])

    @mock.patch('SoftLayer.HardwareManager'
                '.get_available_dedicated_server_packages')
    @mock.patch('SoftLayer.HardwareManager.get_bare_metal_package_id')
    @mock.patch('SoftLayer.HardwareManager.verify_order')
    def test_create_server_test_for_bmc(self, verify_mock, bmpi, packages):
        packages.return_value = [(1099, 'Bare Metal Instance', 'BMC')]
        bmpi.return_value = '1099'

        # First, test the --test flag
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

        result = self.run_command(['server', 'create',
                                   '--chassis=1099',
                                   '--hostname=test',
                                   '--domain=example.com',
                                   '--datacenter=TEST00',
                                   '--cpu=2',
                                   '--memory=2',
                                   '--network=100',
                                   '--disk=250_SATA_II',
                                   '--disk=250_SATA_II',
                                   '--os=UBUNTU_12_64_MINIMAL',
                                   '--vlan-public=10234',
                                   '--vlan-private=20468',
                                   '--key=1234',
                                   '--key=456',
                                   '--test',
                                   '--postinstall='
                                   'http://somescript.foo/myscript.sh',
                                   '--billing=hourly',
                                   ])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("First Item", result.output)
        self.assertIn("Second Item", result.output)
        self.assertIn("Total monthly cost", result.output)

    @mock.patch('SoftLayer.HardwareManager'
                '.get_available_dedicated_server_packages')
    @mock.patch('SoftLayer.HardwareManager.get_bare_metal_package_id')
    @mock.patch('SoftLayer.HardwareManager.place_order')
    def test_create_server_for_bmc(self, order_mock, bmpi, packages):
        order_mock.return_value = {
            'orderId': 98765,
            'orderDate': '2013-08-02 15:23:47'
        }

        result = self.run_command(['--really', 'server', 'create',
                                   '--chassis=1099',
                                   '--hostname=test',
                                   '--domain=example.com',
                                   '--datacenter=TEST00',
                                   '--cpu=4',
                                   '--memory=4',
                                   '--network=100',
                                   '--disk=250_SATA_II',
                                   '--disk=250_SATA_II',
                                   '--os=UBUNTU_12_64_MINIMAL',
                                   '--vlan-public=10234',
                                   '--vlan-private=20468',
                                   '--key=1234',
                                   '--key=456',
                                   '--billing=hourly',
                                   ])

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(json.loads(result.output),
                         {'id': 98765, 'created': '2013-08-02 15:23:47'})

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

        self.assertEqual(result.exit_code, 0)
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

            self.assertEqual(result.exit_code, 0)
            self.assertEqual(result.output, "")
            self.assert_called_with('SoftLayer_Hardware_Server',
                                    'setUserMetadata',
                                    args=(['some data'],),
                                    identifier=1000)

    def test_get_default_value_returns_none_for_unknown_category(self):
        option_mock = {'categories': {'cat1': []}}
        output = create._get_default_value(option_mock, 'nope')
        self.assertEqual(None, output)
