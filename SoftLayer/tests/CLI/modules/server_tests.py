"""
    SoftLayer.tests.CLI.modules.server_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This is a series of integration tests designed to test the complete
    command line interface.

    :license: MIT, see LICENSE for more details.
"""
try:
    # Python 3.x compatibility
    import builtins  # NOQA
    builtins_name = 'builtins'
except ImportError:
    builtins_name = '__builtin__'

import mock

from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer.CLI.modules import server
from SoftLayer import testing
from SoftLayer.testing import fixtures


class ServerCLITests(testing.TestCase):
    def set_up(self):
        self.client = testing.FixtureClient()

    def test_server_cancel_reasons(self):
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
        f(expected, formatting.format_output(output, 'python'))

    @mock.patch('SoftLayer.HardwareManager'
                '.get_available_dedicated_server_packages')
    def test_server_create_options(self, packages):
        args = {
            '<chassis_id>': '999',
            '--all': True,
            '--datacenter': False,
            '--cpu': False,
            '--nic': False,
            '--disk': False,
            '--os': False,
            '--memory': False,
            '--controller': False,
        }

        test_data = [
            (999, 'Chassis 999'),
        ]
        packages.return_value = test_data

        runnable = server.ServerCreateOptions(client=self.client)

        output = runnable.execute(args)

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

        self.assertEqual(expected, formatting.format_output(output, 'python'))

    @mock.patch('SoftLayer.HardwareManager'
                '.get_available_dedicated_server_packages')
    def test_server_create_options_with_cpu_only(self, packages):
        args = {
            '<chassis_id>': '999',
            '--all': False,
            '--datacenter': False,
            '--cpu': True,
            '--nic': False,
            '--disk': False,
            '--os': False,
            '--memory': False,
            '--controller': False,
        }

        test_data = [
            (999, 'Chassis 999'),
        ]
        packages.return_value = test_data

        runnable = server.ServerCreateOptions(client=self.client)

        output = runnable.execute(args)

        expected = {
            'cpu': [
                {'Description': 'Dual Quad Core Pancake 200 - 1.60GHz',
                 'ID': 723},
                {'Description': 'Dual Quad Core Pancake 200 - 1.80GHz',
                 'ID': 724}
            ],
        }

        self.assertEqual(expected, formatting.format_output(output, 'python'))

    @mock.patch('SoftLayer.HardwareManager'
                '.get_available_dedicated_server_packages')
    def test_server_create_options_with_invalid_chassis(self, packages):
        args = {
            '<chassis_id>': '999',
            '--all': True,
            '--datacenter': False,
            '--cpu': False,
            '--nic': False,
            '--disk': False,
            '--os': False,
            '--memory': False,
            '--controller': False,
        }

        test_data = [
            (998, 'Legacy Chassis'),
        ]
        packages.return_value = test_data

        runnable = server.ServerCreateOptions(client=self.client)

        self.assertRaises(exceptions.CLIAbort, runnable.execute, args)

    @mock.patch('SoftLayer.HardwareManager'
                '.get_available_dedicated_server_packages')
    @mock.patch('SoftLayer.HardwareManager.get_bare_metal_package_id')
    def test_server_create_options_for_bmc(self, bmpi, packages):
        args = {
            '<chassis_id>': '1099',
            '--all': True,
            '--datacenter': False,
            '--cpu': False,
            '--nic': False,
            '--disk': False,
            '--os': False,
            '--memory': False,
            '--controller': False,
        }

        test_data = [
            (1099, 'Bare Metal Instance'),
        ]
        packages.return_value = test_data

        bmpi.return_value = '1099'

        runnable = server.ServerCreateOptions(client=self.client)

        output = runnable.execute(args)

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

        self.assertEqual(expected, formatting.format_output(output, 'python'))

    def test_server_details(self):
        runnable = server.ServerDetails(client=self.client)

        args = {'<identifier>': 1234, '--passwords': True, '--price': True}
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

        self.assertEqual(expected, formatting.format_output(output, 'python'))

    def test_server_details_issue_332(self):
        runnable = server.ServerDetails(client=self.client)
        result = fixtures.Hardware_Server.getObject.copy()
        result['primaryIpAddress'] = None
        self.client['Hardware_Server'].getObject.return_value = result

        runnable.execute({'<identifier>': 1234,
                          '--passwords': True,
                          '--price': True})

        self.assertFalse(self.client['Hardware_Server']
                         .getReverseDomainRecords.called)

    def test_list_servers(self):
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
            },
            {
                'datacenter': 'TEST00',
                'primary_ip': '172.16.4.95',
                'host': 'hardware-bad-memory.test.sftlyr.ws',
                'memory': 0,
                'cores': 4,
                'id': 1002,
                'backend_ip': '10.1.0.4',
                'active_transaction': None
            }
        ]

        self.assertEqual(expected, formatting.format_output(output, 'python'))

    @mock.patch('SoftLayer.CLI.formatting.no_going_back')
    @mock.patch('SoftLayer.HardwareManager.reload')
    @mock.patch('SoftLayer.CLI.helpers.resolve_id')
    def test_server_reload(self, resolve_mock, reload_mock, ngb_mock):
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

        self.assertRaises(exceptions.CLIAbort, runnable.execute, args)

    @mock.patch('SoftLayer.CLI.formatting.no_going_back')
    @mock.patch('SoftLayer.HardwareManager.cancel_hardware')
    @mock.patch('SoftLayer.CLI.helpers.resolve_id')
    def test_cancel_server(self, resolve_mock, cancel_mock, ngb_mock):
        hw_id = 12345
        resolve_mock.return_value = hw_id
        ngb_mock.return_value = False
        runnable = server.CancelServer(client=self.client)

        # Check the positive case
        args = {'--really': True, '--reason': 'Test'}
        runnable.execute(args)

        cancel_mock.assert_called_with(hw_id, args['--reason'], None)

        # Now check to make sure we properly call CLIAbort in the negative case
        env_mock = mock.Mock()
        env_mock.input = mock.Mock()
        env_mock.input.return_value = 'Comment'

        args['--really'] = False
        runnable = server.CancelServer(client=self.client, env=env_mock)

        self.assertRaises(exceptions.CLIAbort, runnable.execute, args)
        env_mock.assert_called()

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_server_power_off(self, confirm_mock):
        hw_id = 12345
        runnable = server.ServerPowerOff(client=self.client)

        # Check the positive case
        args = {'--really': True, '<identifier>': '12345'}

        runnable.execute(args)

        self.client['Hardware_Server'].powerOff.assert_called_with(id=hw_id)

        # Now check to make sure we properly call CLIAbort in the negative case
        confirm_mock.return_value = False
        args['--really'] = False
        self.assertRaises(exceptions.CLIAbort, runnable.execute, args)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_server_reboot(self, confirm_mock):
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
        self.assertRaises(exceptions.CLIAbort, runnable.execute, args)

    def test_server_power_on(self):
        hw_id = 12345
        runnable = server.ServerPowerOn(client=self.client)

        # Check the positive case
        args = {
            '<identifier>': '12345',
        }

        runnable.execute(args)
        self.client['Hardware_Server'].powerOn.assert_called_with(id=hw_id)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_server_power_cycle(self, confirm_mock):
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
        self.assertRaises(exceptions.CLIAbort, runnable.execute, args)

    @mock.patch('SoftLayer.HardwareManager.change_port_speed')
    @mock.patch('SoftLayer.CLI.helpers.resolve_id')
    def test_cic_edit_server(self, resolve_mock, port_mock):
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

    @mock.patch('SoftLayer.HardwareManager'
                '.get_available_dedicated_server_packages')
    def test_list_chassis_server(self, packages):
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

        self.assertEqual(expected, formatting.format_output(output, 'python'))

    def test_create_server(self):
        args = {
            '--chassis': 999,
            '--hostname': 'test',
            '--domain': 'example.com',
            '--datacenter': 'TEST00',
            '--cpu': False,
            '--network': '100',
            '--disk': ['250_SATA_II', '250_SATA_II'],
            '--os': 'UBUNTU_12_64_MINIMAL',
            '--memory': False,
            '--controller': False,
            '--test': True,
            '--export': None,
            '--template': None,
            '--key': [1234, 456],
            '--vlan_public': 10234,
            '--vlan_private': 20468,
            '--postinstall': 'http://somescript.foo/myscript.sh',
        }

        runnable = server.CreateServer(client=self.client)

        # First, test the --test flag
        with mock.patch('SoftLayer.HardwareManager'
                        '.verify_order') as verify_mock:
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

            self.assertEqual(expected,
                             formatting.format_output(output, 'python'))

            # Make sure we can order without specifying the disk as well
            args['--disk'] = []

            output = runnable.execute(args)

            self.assertEqual(expected,
                             formatting.format_output(output, 'python'))

            # Test explicitly setting a RAID configuration
            args['--controller'] = 'RAID0'

            output = runnable.execute(args)

            self.assertEqual(expected,
                             formatting.format_output(output, 'python'))

        # Now test ordering
        with mock.patch('SoftLayer.HardwareManager.place_order') as order_mock:
            order_mock.return_value = {
                'orderId': 98765,
                'orderDate': '2013-08-02 15:23:47'
            }

            args['--test'] = False
            args['--really'] = True

            output = runnable.execute(args)

            expected = {'id': 98765, 'created': '2013-08-02 15:23:47'}
            self.assertEqual(expected,
                             formatting.format_output(output, 'python'))

        # Finally, test cancelling the process
        with mock.patch('SoftLayer.CLI.formatting.confirm') as confirm:
            confirm.return_value = False

            args['--really'] = False

            self.assertRaises(exceptions.CLIAbort, runnable.execute, args)

    def test_create_server_failures(self):

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

        runnable = server.CreateServer(client=self.client)

        # Verify that ArgumentError is properly raised on error
        self.assertRaises(exceptions.ArgumentError, runnable.execute, args)

        # This contains an invalid network argument
        args['--chassis'] = 999
        args['--network'] = 9999

        # Verify that CLIAbort is properly raised on error
        self.assertRaises(exceptions.CLIAbort, runnable.execute, args)

        # This contains an invalid operating system argument
        args['--network'] = '100'
        args['--os'] = 'nope'

        # Verify that CLIAbort is properly raised on error
        self.assertRaises(exceptions.CLIAbort, runnable.execute, args)

    @mock.patch('SoftLayer.CLI.template.export_to_template')
    def test_create_server_with_export(self, export_to_template):
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

        runnable = server.CreateServer(client=self.client)

        expected = args.copy()
        del(expected['--export'])

        runnable.execute(args)

        export_to_template.assert_called_with('test_file.txt', expected,
                                              exclude=['--wait', '--test'])

    @mock.patch('SoftLayer.HardwareManager'
                '.get_available_dedicated_server_packages')
    @mock.patch('SoftLayer.HardwareManager.get_bare_metal_package_id')
    def test_create_server_for_bmc(self, bmpi, packages):
        args = {
            '--chassis': '1099',
            '--hostname': 'test',
            '--domain': 'example.com',
            '--datacenter': 'TEST00',
            '--cpu': '2',
            '--network': '100',
            '--disk': ['250_SATA_II', '250_SATA_II'],
            '--os': 'UBUNTU_12_64_MINIMAL',
            '--memory': '2',
            '--test': True,
            '--export': None,
            '--template': None,
            '--key': [1234, 456],
            '--vlan_public': 10234,
            '--vlan_private': 20468,
            '--postinstall': 'http://somescript.foo/myscript.sh',
            '--billing': 'hourly',
        }

        test_data = [
            (1099, 'Bare Metal Instance'),
        ]
        packages.return_value = test_data

        bmpi.return_value = '1099'

        runnable = server.CreateServer(client=self.client)

        # First, test the --test flag
        with mock.patch('SoftLayer.HardwareManager'
                        '.verify_order') as verify_mock:
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

            self.assertEqual(expected,
                             formatting.format_output(output, 'python'))

            # Make sure we can order without specifying the disk as well
            args['--disk'] = []

            output = runnable.execute(args)

            self.assertEqual(expected,
                             formatting.format_output(output, 'python'))

            # Test explicitly setting a RAID configuration
            args['--controller'] = 'RAID0'

            output = runnable.execute(args)

            self.assertEqual(expected,
                             formatting.format_output(output, 'python'))

        # Now test ordering
        with mock.patch('SoftLayer.HardwareManager.place_order') as order_mock:
            order_mock.return_value = {
                'orderId': 98765,
                'orderDate': '2013-08-02 15:23:47'
            }

            args['--test'] = False
            args['--really'] = True

            output = runnable.execute(args)

            expected = {'id': 98765, 'created': '2013-08-02 15:23:47'}
            self.assertEqual(expected,
                             formatting.format_output(output, 'python'))

        # Finally, test cancelling the process
        with mock.patch('SoftLayer.CLI.formatting.confirm') as confirm:
            confirm.return_value = False

            args['--really'] = False

            self.assertRaises(exceptions.CLIAbort, runnable.execute, args)

    def test_edit_server(self):
        # Test both userdata and userfile at once
        args = {
            '<identifier>': 1000,
            '--hostname': 'hardware-test1',
            '--domain': 'test.sftlyr.ws',
            '--userdata': 'My data',
            '--userfile': 'my_file.txt',
        }
        runnable = server.EditServer(client=self.client)

        self.assertRaises(exceptions.ArgumentError, runnable.execute, args)

        # Simulate a missing file error
        args['--userdata'] = None

        with mock.patch('os.path.exists') as exists:
            exists.return_value = False

            self.assertRaises(exceptions.ArgumentError, runnable.execute, args)

        # Test a successful edit with user data
        args['--userdata'] = 'My data'
        args['--userfile'] = None

        expected = {
            'userdata': 'My data',
            'domain': 'test.sftlyr.ws',
            'hostname': 'hardware-test1',
        }

        with mock.patch('SoftLayer.HardwareManager.edit') as edit_mock:
            edit_mock.return_value = True

            runnable.execute(args)

            edit_mock.assert_called_with(1000, **expected)

            # Now check for a CLIAbort if there's an error
            edit_mock.return_value = False

            self.assertRaises(exceptions.CLIAbort, runnable.execute, args)

        # Test a successful edit with a user file
        args['--userdata'] = None
        args['--userfile'] = 'my_file.txt'

        expected = {
            'userdata': 'My data',
            'domain': 'test.sftlyr.ws',
            'hostname': 'hardware-test1',
        }

        with mock.patch('os.path.exists') as exists:
            exists.return_value = True
            with mock.patch(builtins_name + '.open') as file_mock:
                file_mock.return_value.__enter__ = lambda s: s
                file_mock.return_value.__exit__ = mock.Mock()
                file_mock.return_value.read.return_value = 'some data'

                with mock.patch('SoftLayer.HardwareManager.edit') as edit_mock:
                    edit_mock.return_value = True
                    expected['userdata'] = 'some data'

                    runnable.execute(args)

                    edit_mock.assert_called_with(1000, **expected)

    def test_get_default_value_returns_none_for_unknown_category(self):
        option_mock = {'categories': {'cat1': []}}
        runnable = server.CreateServer()
        output = runnable._get_default_value(option_mock, 'nope')
        self.assertEqual(None, output)
