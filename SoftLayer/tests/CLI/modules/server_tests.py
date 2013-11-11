"""
    SoftLayer.tests.CLI.modules.server_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This is a series of integration tests designed to test the complete
    command line interface.

    :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
    :license: MIT, see LICENSE for more details.
"""
from SoftLayer.tests import unittest
from mock import Mock, MagicMock, patch
try:
    # Python 3.x compatibility
    import builtins
    builtins_name = 'builtins'
except ImportError:
    builtins_name = '__builtin__'

from SoftLayer.CLI.helpers import format_output, CLIAbort, ArgumentError
from SoftLayer.CLI.modules import server
from SoftLayer.tests.mocks import (
    account_mock, hardware_mock, product_package_mock)


class ServerCLITests(unittest.TestCase):
    def setUp(self):
        self.client = MagicMock()

    def test_ServerCancelReasons(self):
        runnable = server.ServerCancelReasons(client=self.client)
        output = runnable.execute({})

        expected = [
            {'Code': 'datacenter',
             'Reason': 'Migrating to a different SoftLayer datacenter'},
            {'Code': 'cost', 'Reason': 'Server / Upgrade Costs'},
            {'Code': 'moving', 'Reason': 'Moving to competitor'},
            {'Code': 'migrate_smaller',
             'Reason': 'Migrating to smaller server'},
            {'Code': 'sales', 'Reason': 'Sales process / upgrades'},
            {'Code': 'performance',
             'Reason': 'Network performance / latency'},
            {'Code': 'unneeded', 'Reason': 'No longer needed'},
            {'Code': 'support', 'Reason': 'Support response / timing'},
            {'Code': 'closing', 'Reason': 'Business closing down'},
            {'Code': 'migrate_larger', 'Reason': 'Migrating to larger server'}
        ]

        method = 'assertItemsEqual'
        if not hasattr(self, method):
            # For Python 3.3 compatibility
            method = 'assertCountEqual'

        f = getattr(self, method)
        f(expected, format_output(output, 'python'))

    def test_ServerCreateOptions(self):
        args = {
            '<chassis_id>': 999,
            '--all': True,
            '--datacenter': False,
            '--cpu': False,
            '--nic': False,
            '--disk': False,
            '--os': False,
            '--memory': False,
            '--controller': False,
        }

        client = self._setup_package_mocks(self.client)
        runnable = server.ServerCreateOptions(client=client)

        output = runnable.execute(args)

        expected = {
            'datacenter': ['RANDOM_LOCATION'],
            'dual nic': ['100_DUAL', '10_DUAL'],
            'disk_controllers': ['None', 'RAID0'],
            'os (CENTOS)': ['CENTOS_6_64'],
            'os (DEBIAN)': ['DEBIAN_6_32'],
            'os (REDHAT)': ['REDHAT_6_64_6'],
            'os (UBUNTU)': ['UBUNTU_12_64', 'UBUNTU_12_64_MINIMAL'],
            'os (WIN)': ['WIN_2003-STD-R2_64', 'WIN_2008-DC-HYPERV_64',
                         'WIN_2008-ENT_64', 'WIN_2008-STD_64'],
            'memory': [4, 6],
            'disk': ['1000_DRIVE'],
            'single nic': ['100', '1000'],
            'cpu': [
                {'description': 'Dual Quad Core Pancake 200 - 1.60GHz',
                 'id': 723},
                {'description': 'Dual Quad Core Pancake 200 - 1.80GHz',
                 'id': 724}
            ],
        }

        self.assertEqual(expected, format_output(output, 'python'))

    def test_ServerCreateOptions_with_cpu_only(self):
        args = {
            '<chassis_id>': 999,
            '--all': False,
            '--datacenter': False,
            '--cpu': True,
            '--nic': False,
            '--disk': False,
            '--os': False,
            '--memory': False,
            '--controller': False,
        }

        client = self._setup_package_mocks(self.client)
        runnable = server.ServerCreateOptions(client=client)

        output = runnable.execute(args)

        expected = {
            'cpu': [
                {'description': 'Dual Quad Core Pancake 200 - 1.60GHz',
                 'id': 723},
                {'description': 'Dual Quad Core Pancake 200 - 1.80GHz',
                 'id': 724}
            ],
        }

        self.assertEqual(expected, format_output(output, 'python'))

    def test_ServerDetails(self):
        hw_id = 1234

        client = Mock()
        client.__getitem__ = Mock()
        service = client['Hardware_Server']
        service.getObject = hardware_mock.getObject_Mock(1000)
        dns_mock = hardware_mock.getReverseDomainRecords_Mock(1000)
        service.getReverseDomainRecords = dns_mock
        runnable = server.ServerDetails(client=client)

        args = {'<identifier>': hw_id, '--passwords': True, '--price': True}
        output = runnable.execute(args)

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
                      {'id': 19082, 'number': 3672, 'type': 'PUBLIC'}]
        }

        self.assertEqual(expected, format_output(output, 'python'))

    def test_ListServers(self):
        self.client['Account'].getHardware = account_mock.getHardware_Mock()
        runnable = server.ListServers(client=self.client)

        output = runnable.execute({'--tags': 'openstack'})

        expected = [
            {
                'datacenter': 'TEST00',
                'primary_ip': '172.16.1.100',
                'host': 'hardware-test1.test.sftlyr.ws',
                'memory': 2048,
                'cores': 2,
                'id': 1000,
                'backend_ip': '10.1.0.2',
                'active_transaction': 'TXN_NAME'
            },
            {
                'datacenter': 'TEST00',
                'primary_ip': '172.16.4.94',
                'host': 'hardware-test2.test.sftlyr.ws',
                'memory': 4096,
                'cores': 4,
                'id': 1001,
                'backend_ip': '10.1.0.3',
                'active_transaction': None
            }
        ]

        self.assertEqual(expected, format_output(output, 'python'))

    @patch('SoftLayer.CLI.modules.server.CLIAbort')
    @patch('SoftLayer.CLI.modules.server.no_going_back')
    @patch('SoftLayer.HardwareManager.reload')
    @patch('SoftLayer.CLI.modules.server.resolve_id')
    def test_ServerReload(
            self, resolve_mock, reload_mock, ngb_mock, abort_mock):
        hw_id = 12345
        resolve_mock.return_value = hw_id
        ngb_mock.return_value = False
        runnable = server.ServerReload(client=self.client)

        # Check the positive case
        args = {'--really': True, '--postinstall': None, '--key': [12345]}
        runnable.execute(args)

        reload_mock.assert_called_with(hw_id, args['--postinstall'], [12345])

        # Now check to make sure we properly call CLIAbort in the negative case
        args['--really'] = False

        runnable.execute(args)
        abort_mock.assert_called()

    @patch('SoftLayer.CLI.modules.server.CLIAbort')
    @patch('SoftLayer.CLI.modules.server.no_going_back')
    @patch('SoftLayer.HardwareManager.cancel_hardware')
    @patch('SoftLayer.CLI.modules.server.resolve_id')
    def test_CancelServer(
            self, resolve_mock, cancel_mock, ngb_mock, abort_mock):
        hw_id = 12345
        resolve_mock.return_value = hw_id
        ngb_mock.return_value = False
        runnable = server.CancelServer(client=self.client)

        # Check the positive case
        args = {'--really': True, '--reason': 'Test'}
        runnable.execute(args)

        cancel_mock.assert_called_with(hw_id, args['--reason'], None)

        # Now check to make sure we properly call CLIAbort in the negative case
        env_mock = Mock()
        env_mock.input = Mock()
        env_mock.input.return_value = 'Comment'

        args['--really'] = False
        runnable = server.CancelServer(client=self.client, env=env_mock)

        runnable.execute(args)
        abort_mock.assert_called()
        env_mock.assert_called()

    @patch('SoftLayer.CLI.modules.server.confirm')
    def test_ServerPowerOff(self, confirm_mock):
        hw_id = 12345
        runnable = server.ServerPowerOff(client=self.client)

        # Check the positive case
        args = {'--really': True, '<identifier>': '12345'}

        runnable.execute(args)

        self.client['Hardware_Server'].powerOff.assert_called_with(id=hw_id)

        # Now check to make sure we properly call CLIAbort in the negative case
        confirm_mock.return_value = False
        args['--really'] = False
        self.assertRaises(CLIAbort, runnable.execute, args)

    @patch('SoftLayer.CLI.modules.server.confirm')
    def test_ServerReboot(self, confirm_mock):
        hw_id = 12345
        runnable = server.ServerReboot(client=self.client)

        # Check the positive case
        args = {
            '--really': True,
            '<identifier>': '12345',
            '--hard': False,
            '--soft': False,
        }

        runnable.execute(args)
        self.client['Hardware_Server'].rebootDefault.assert_called_with(
            id=hw_id)

        args['--soft'] = True
        args['--hard'] = False
        runnable.execute(args)
        self.client['Hardware_Server'].rebootSoft.assert_called_with(id=hw_id)

        args['--soft'] = False
        args['--hard'] = True
        runnable.execute(args)
        self.client['Hardware_Server'].rebootHard.assert_called_with(id=hw_id)

        # Now check to make sure we properly call CLIAbort in the negative case
        confirm_mock.return_value = False
        args['--really'] = False
        self.assertRaises(CLIAbort, runnable.execute, args)

    def test_ServerPowerOn(self):
        hw_id = 12345
        runnable = server.ServerPowerOn(client=self.client)

        # Check the positive case
        args = {
            '<identifier>': '12345',
        }

        runnable.execute(args)
        self.client['Hardware_Server'].powerOn.assert_called_with(id=hw_id)

    @patch('SoftLayer.CLI.modules.server.confirm')
    def test_ServerPowerCycle(self, confirm_mock):
        hw_id = 12345
        runnable = server.ServerPowerCycle(client=self.client)

        # Check the positive case
        args = {
            '<identifier>': '12345',
            '--really': True,
        }

        runnable.execute(args)
        self.client['Hardware_Server'].powerCycle.assert_called_with(id=hw_id)

        # Now check to make sure we properly call CLIAbort in the negative case
        confirm_mock.return_value = False
        args['--really'] = False
        self.assertRaises(CLIAbort, runnable.execute, args)

    @patch('SoftLayer.HardwareManager.change_port_speed')
    @patch('SoftLayer.CLI.modules.server.resolve_id')
    def test_NicEditServer(self, resolve_mock, port_mock):
        hw_id = 12345
        resolve_mock.return_value = hw_id

        # Test updating the port
        args = {
            'port': True,
            'public': False,
            'private': True,
            '--speed': 100
        }

        port_mock.side_effect = [True, False]
        runnable = server.NicEditServer(client=self.client)

        # First call simulates a success
        runnable.execute(args)
        port_mock.assert_called_with(hw_id, False, 100)

        # Second call simulates an error
        runnable.execute(args)

    @patch('SoftLayer.HardwareManager.get_available_dedicated_server_packages')
    def test_ListChassisServer(self, packages):
        test_data = [
            (1, 'Chassis 1'),
            (2, 'Chassis 2')
        ]
        packages.return_value = test_data
        runnable = server.ListChassisServer(client=self.client)

        output = runnable.execute({})

        expected = [
            {'Chassis': 'Chassis 1', 'Code': 1},
            {'Chassis': 'Chassis 2', 'Code': 2}
        ]

        self.assertEqual(expected, format_output(output, 'python'))

    def test_CreateServer(self):
        args = {
            '--chassis': 999,
            '--hostname': 'test',
            '--domain': 'example.com',
            '--datacenter': 'TEST00',
            '--cpu': False,
            '--network': '100',
            '--disk': ['1000_DRIVE', '1000_DRIVE'],
            '--os': 'UBUNTU_12_64_MINIMAL',
            '--memory': False,
            '--controller': False,
            '--test': True,
            '--export': None,
            '--template': None,
            '--key': [1234, 456],
            '--vlan_public': 10234,
            '--vlan_private': 20468,
        }

        client = self._setup_package_mocks(self.client)
        runnable = server.CreateServer(client=client)

        # First, test the --test flag
        with patch('SoftLayer.HardwareManager.verify_order') as verify_mock:
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
            output = runnable.execute(args)

            expected = [
                [
                    {'Item': 'First Item', 'cost': '0.00'},
                    {'Item': 'Second Item', 'cost': '25.00'},
                    {'Item': 'Total monthly cost', 'cost': '25.00'}
                ],
                ''
            ]

            self.assertEqual(expected, format_output(output, 'python'))

            # Make sure we can order without specifying the disk as well
            args['--disk'] = []

            output = runnable.execute(args)

            self.assertEqual(expected, format_output(output, 'python'))

            # And make sure we can pass in disk and SSH keys as comma separated
            # strings, which is what templates do
            args['--disk'] = '1000_DRIVE,1000_DRIVE'
            args['--key'] = '123,456'

            output = runnable.execute(args)

            self.assertEqual(expected, format_output(output, 'python'))

            # Test explicitly setting a RAID configuration
            args['--controller'] = 'RAID0'

            output = runnable.execute(args)

            self.assertEqual(expected, format_output(output, 'python'))

        # Now test ordering
        with patch('SoftLayer.HardwareManager.place_order') as order_mock:
            order_mock.return_value = {
                'orderId': 98765,
                'orderDate': '2013-08-02 15:23:47'
            }

            args['--test'] = False
            args['--really'] = True

            output = runnable.execute(args)

            expected = {'id': 98765, 'created': '2013-08-02 15:23:47'}
            self.assertEqual(expected, format_output(output, 'python'))

        # Finally, test cancelling the process
        with patch('SoftLayer.CLI.modules.server.confirm') as confirm:
            confirm.return_value = False

            args['--really'] = False

            self.assertRaises(CLIAbort, runnable.execute, args)

    def test_CreateServer_failures(self):
        client = self._setup_package_mocks(self.client)

        # This is missing a required argument
        args = {
            '--hostname': 'test',
            '--domain': 'example.com',
            '--datacenter': 'TEST00',
            '--cpu': False,
            '--disk': ['1000_DRIVE', '1000_DRIVE'],
            '--os': 'UBUNTU_12_64_MINIMAL',
            '--memory': False,
            '--controller': False,
            '--test': True,
            '--export': None,
            '--template': None,
        }

        runnable = server.CreateServer(client=client)

        # Verify that ArgumentError is properly raised on error
        self.assertRaises(ArgumentError, runnable.execute, args)

        # This contains an invalid network argument
        args['--chassis'] = 999
        args['--network'] = 9999

        # Verify that CLIAbort is properly raised on error
        self.assertRaises(CLIAbort, runnable.execute, args)

        # This contains an invalid operating system argument
        args['--network'] = '100'
        args['--os'] = 'nope'

        # Verify that CLIAbort is properly raised on error
        self.assertRaises(CLIAbort, runnable.execute, args)

    @patch('SoftLayer.CLI.modules.server.export_to_template')
    def test_CreateServer_with_export(self, export_to_template):
        args = {
            '--chassis': 999,
            '--hostname': 'test',
            '--domain': 'example.com',
            '--datacenter': 'TEST00',
            '--cpu': False,
            '--network': '100',
            '--disk': ['1000_DRIVE', '1000_DRIVE'],
            '--os': 'UBUNTU_12_64_MINIMAL',
            '--memory': False,
            '--controller': False,
            '--test': True,
            '--template': None,
            '--key': [1234],
            '--export': 'test_file.txt',
        }

        client = self._setup_package_mocks(self.client)
        runnable = server.CreateServer(client=client)

        expected = args.copy()
        del(expected['--export'])

        runnable.execute(args)

        export_to_template.assert_called_with('test_file.txt', expected,
                                              exclude=['--wait', '--test'])

    def test_EditServer(self):
        # Test both userdata and userfile at once
        args = {
            '<identifier>': 1000,
            '--hostname': 'hardware-test1',
            '--domain': 'test.sftlyr.ws',
            '--userdata': 'My data',
            '--userfile': 'my_file.txt',
        }
        runnable = server.EditServer(client=self.client)

        self.assertRaises(ArgumentError, runnable.execute, args)

        # Simulate a missing file error
        args['--userdata'] = None

        with patch('os.path.exists') as exists:
            exists.return_value = False

            self.assertRaises(ArgumentError, runnable.execute, args)

        # Test a successful edit with user data
        args['--userdata'] = 'My data'
        args['--userfile'] = None

        expected = {
            'userdata': 'My data',
            'domain': 'test.sftlyr.ws',
            'hostname': 'hardware-test1',
        }

        with patch('SoftLayer.HardwareManager.edit') as edit_mock:
            edit_mock.return_value = True

            runnable.execute(args)

            edit_mock.assert_called_with(1000, **expected)

            # Now check for a CLIAbort if there's an error
            edit_mock.return_value = False

            self.assertRaises(CLIAbort, runnable.execute, args)

        # Test a successful edit with a user file
        args['--userdata'] = None
        args['--userfile'] = 'my_file.txt'

        expected = {
            'userdata': 'My data',
            'domain': 'test.sftlyr.ws',
            'hostname': 'hardware-test1',
        }

        with patch('os.path.exists') as exists:
            exists.return_value = True
            with patch(builtins_name + '.open') as file_mock:
                file_mock.return_value.__enter__ = lambda s: s
                file_mock.return_value.__exit__ = Mock()
                file_mock.return_value.read.return_value = 'some data'

                with patch('SoftLayer.HardwareManager.edit') as edit_mock:
                    edit_mock.return_value = True
                    expected['userdata'] = 'some data'

                    runnable.execute(args)

                    edit_mock.assert_called_with(1000, **expected)

    def test_get_default_value_returns_none_for_unknown_category(self):
        option_mock = {'categories': {'cat1': []}}
        runnable = server.CreateServer()
        output = runnable._get_default_value(option_mock, 'nope')
        self.assertEqual(None, output)

    @staticmethod
    def _setup_package_mocks(client):
        package = client['Product_Package']
        package.getAllObjects = product_package_mock.getAllObjects_Mock()
        package.getConfiguration = product_package_mock.getConfiguration_Mock()
        package.getCategories = product_package_mock.getCategories_Mock()
        package.getRegions = product_package_mock.getRegions_Mock()

        return client
