"""
    tests.CLI.modules.hardware_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This is a series of integration tests designed to test the complete
    command line interface.

    :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
    :license: BSD, see LICENSE for more details.
"""
try:
    import unittest2 as unittest
except ImportError:
    import unittest  # NOQA
from mock import Mock, MagicMock, patch

from SoftLayer.CLI.helpers import format_output, CLIAbort
from SoftLayer.CLI.modules import server
#from SoftLayer.CLI.modules.hardware import *
from tests.mocks import account_mock


class HardwareCLITests(unittest.TestCase):
    def setUp(self):
        self.client = MagicMock()

    @patch('SoftLayer.HardwareManager.get_cancellation_reasons')
    def test_HardwareCancelReasons(self, reasons):
        test_data = {
            'code1': 'Reason 1',
            'code2': 'Reason 2'
        }
        reasons.return_value = test_data

        output = server.ServerCancelReasons.execute(self.client, {})

        expected = [{'Reason': 'Reason 1', 'Code': 'code1'},
                    {'Reason': 'Reason 2', 'Code': 'code2'}]

        self.assertEqual(expected, format_output(output, 'python'))

    @patch('SoftLayer.HardwareManager.get_dedicated_server_create_options')
    def test_HardwareCreateOptions(self, create_options):
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

        # This test data represents the structure of the information returned
        # by HardwareManager.get_dedicated_server_create_options.
        test_data = self.get_create_options_data()

        create_options.return_value = test_data

        output = server.ServerCreateOptions.execute(self.client, args)

        expected = {
            'datacenter': ['FIRST_AVAILABLE', 'TEST00'],
            'dual nic': ['100_DUAL'],
            'disk_controllers': ['RAID5'],
            'os (CLOUDLINUX)': ['CLOUDLINUX_5_32_MINIMAL'],
            'os (WIN)': ['WIN_2012-DC-HYPERV_64'],
            'memory': [2, 4],
            'disk': ['100_SATA'],
            'single nic': ['100'],
            'cpu': [{'id': 1, 'description': 'CPU Core'}],
            'os (UBUNTU)': ['UBUNTU_10_32']
        }

        self.assertEqual(expected, format_output(output, 'python'))

    @patch('SoftLayer.HardwareManager.get_hardware')
    def test_HardwareDetails(self, get_hardware):
        hw_id = 1234

        servers = self.get_server_mocks()
        get_hardware.return_value = servers[0]

        dns_mock = Mock()
        dns_mock.getReverseDomainRecords = Mock()
        dns_mock.getReverseDomainRecords.return_value = [{
            'resourceRecords': [{'data': '2.0.0.10.in-addr.arpa'}]
        }]
        client = Mock()
        client.__getitem__ = Mock()
        client.__getitem__.return_value = dns_mock

        args = {'<identifier>': hw_id, '--passwords': True}
        output = server.ServerDetails.execute(client, args)

        expected = {
            'status': 'ACTIVE',
            'datacenter': 'TEST00',
            'created': '2013-08-01 15:23:45',
            'notes': 'These are test notes.',
            'hostname': 'test1.sftlyr.ws',
            'public_ip': '10.0.0.2',
            'private_ip': '10.1.0.2',
            'memory': 2048,
            'cores': 2,
            'ptr': '2.0.0.10.in-addr.arpa',
            'os': 'Ubuntu', 'id': 1,
            'users': ['root abc123'],
            'vlans': [{'id': 9653, 'number': 1800, 'type': 'PRIVATE'},
                      {'id': 19082, 'number': 3672, 'type': 'PUBLIC'}]
        }

        self.assertEqual(expected, format_output(output, 'python'))

    def test_ListHardware(self):
        self.client['Account'].getHardware = account_mock.getHardware_Mock()

        output = server.ListServers.execute(
            self.client, {'--tags': 'openstack'})

        expected = [
            {
                'datacenter': 'TEST00',
                'primary_ip': '172.16.1.100',
                'host': 'hardware-test1.test.sftlyr.ws',
                'memory': 2048,
                'cores': 2,
                'id': 1000,
                'backend_ip': '10.1.0.2'
            },
            {
                'datacenter': 'TEST00',
                'primary_ip': '172.16.4.94',
                'host': 'hardware-test2.test.sftlyr.ws',
                'memory': 4096,
                'cores': 4,
                'id': 1001,
                'backend_ip': '10.1.0.3'
            }
        ]

        self.assertEqual(expected, format_output(output, 'python'))

    @patch('SoftLayer.CLI.modules.server.CLIAbort')
    @patch('SoftLayer.CLI.modules.server.no_going_back')
    @patch('SoftLayer.HardwareManager.reload')
    @patch('SoftLayer.CLI.modules.server.resolve_id')
    def test_HardwareReload(
            self, resolve_mock, reload_mock, ngb_mock, abort_mock):
        hw_id = 12345
        resolve_mock.return_value = hw_id
        ngb_mock.return_value = False

        # Check the positive case
        args = {'--really': True, '--postinstall': None}
        server.ServerReload.execute(self.client, args)

        reload_mock.assert_called_with(hw_id, args['--postinstall'])

        # Now check to make sure we properly call CLIAbort in the negative case
        args['--really'] = False

        server.ServerReload.execute(self.client, args)
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

        env_mock = Mock()
        env_mock.input = Mock()
        env_mock.input.return_value = 'Comment'

        server.CancelServer.env = env_mock
        env_mock.assert_called()

        # Check the positive case
        args = {'--really': True, '--reason': 'Test'}
        server.CancelServer.execute(self.client, args)

        cancel_mock.assert_called_with(hw_id, args['--reason'], 'Comment')

        # Now check to make sure we properly call CLIAbort in the negative case
        env_mock.reset_mock()
        args['--really'] = False

        server.CancelServer.execute(self.client, args)
        abort_mock.assert_called()
        env_mock.assert_called()

    @patch('SoftLayer.CLI.modules.server.confirm')
    def test_ServerPowerOff(self, confirm_mock):
        hw_id = 12345

        # Check the positive case
        args = {'--really': True, '<identifier>': '12345'}

        server.ServerPowerOff.execute(self.client, args)

        self.client['Hardware_Server'].powerOff.assert_called_with(id=hw_id)

        # Now check to make sure we properly call CLIAbort in the negative case
        confirm_mock.return_value = False
        args['--really'] = False
        self.assertRaises(CLIAbort,
                          server.ServerPowerOff.execute, self.client, args)

    @patch('SoftLayer.CLI.modules.server.confirm')
    def test_ServerReboot(self, confirm_mock):
        hw_id = 12345

        # Check the positive case
        args = {
            '--really': True,
            '<identifier>': '12345',
            '--hard': False,
            '--soft': False,
        }

        server.ServerReboot.execute(self.client, args)
        self.client['Hardware_Server'].rebootDefault.assert_called_with(
            id=hw_id)

        args['--soft'] = True
        args['--hard'] = False
        server.ServerReboot.execute(self.client, args)
        self.client['Hardware_Server'].rebootSoft.assert_called_with(id=hw_id)

        args['--soft'] = False
        args['--hard'] = True
        server.ServerReboot.execute(self.client, args)
        self.client['Hardware_Server'].rebootHard.assert_called_with(id=hw_id)

        # Now check to make sure we properly call CLIAbort in the negative case
        confirm_mock.return_value = False
        args['--really'] = False
        self.assertRaises(CLIAbort,
                          server.ServerReboot.execute, self.client, args)

    def test_ServerPowerOn(self):
        hw_id = 12345

        # Check the positive case
        args = {
            '<identifier>': '12345',
        }

        server.ServerPowerOn.execute(self.client, args)
        self.client['Hardware_Server'].powerOn.assert_called_with(id=hw_id)

    @patch('SoftLayer.CLI.modules.server.confirm')
    def test_ServerPowerCycle(self, confirm_mock):
        hw_id = 12345

        # Check the positive case
        args = {
            '<identifier>': '12345',
            '--really': True,
        }

        server.ServerPowerCycle.execute(self.client, args)
        self.client['Hardware_Server'].powerCycle.assert_called_with(id=hw_id)

        # Now check to make sure we properly call CLIAbort in the negative case
        confirm_mock.return_value = False
        args['--really'] = False
        self.assertRaises(CLIAbort,
                          server.ServerPowerCycle.execute, self.client, args)

    @patch('SoftLayer.HardwareManager.change_port_speed')
    @patch('SoftLayer.CLI.modules.server.resolve_id')
    def test_NicEditServer(
            self, resolve_mock, port_mock):
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

        # First call simulates a success
        server.NicEditServer.execute(self.client, args)
        port_mock.assert_called_with(hw_id, False, 100)

        # Second call simulates an error
        self.assertFalse(server.NicEditServer.execute(self.client, args))

    @patch('SoftLayer.HardwareManager.get_available_dedicated_server_packages')
    def test_ListChassisServer(self, packages):
        test_data = [
            (1, 'Chassis 1'),
            (2, 'Chassis 2')
        ]
        packages.return_value = test_data

        output = server.ListChassisServer.execute(self.client, {})

        expected = [
            {'Chassis': 'Chassis 1', 'Code': 1},
            {'Chassis': 'Chassis 2', 'Code': 2}
        ]

        self.assertEqual(expected, format_output(output, 'python'))

    @patch('SoftLayer.HardwareManager.get_dedicated_server_create_options')
    def test_CreateHardware(self, create_options):
        args = {
            '--chassis': 999,
            '--hostname': 'test',
            '--domain': 'example.com',
            '--datacenter': 'TEST00',
            '--cpu': False,
            '--network': '100',
            '--disk': ['100_SATA', '100_SATA'],
            '--os': 'CLOUDLINUX_5_32_MINIMAL',
            '--memory': False,
            '--controller': False,
            '--test': True,
            '--export': None,
            '--template': None,
        }

        # This test data represents the structure of the information returned
        # by HardwareManager.get_dedicated_server_create_options.
        test_data = self.get_create_options_data()

        create_options.return_value = test_data

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
            output = server.CreateServer.execute(self.client, args)

            # This test is fragile. We need to figure out why format 'python'
            # doesn't work here in the CLI code.
            expected = """:....................:.......:
:               Item :  cost :
:....................:.......:
:         First Item :  0.00 :
:        Second Item : 25.00 :
: Total monthly cost : 25.00 :
:....................:.......:
 -- ! Prices reflected here are retail and do not take account level discounts and are not guaranteed."""
            self.assertEqual(expected, format_output(output, 'table'))

        # Now test ordering
        with patch('SoftLayer.HardwareManager.place_order') as order_mock:
            order_mock.return_value = {
                'orderId': 98765,
                'orderDate': '2013-08-02 15:23:47'
            }

            args['--test'] = False
            args['--really'] = True

            output = server.CreateServer.execute(self.client, args)

            expected = {'id': 98765, 'created': '2013-08-02 15:23:47'}
            self.assertEqual(expected, format_output(output, 'python'))

        # Finally, test cancelling the process
        with patch('SoftLayer.CLI.modules.server.confirm') as confirm:
            confirm.return_value = False

            args['--really'] = False

            self.assertRaises(CLIAbort,
                              server.CreateServer.execute, self.client, args)

    @staticmethod
    def get_create_options_data():
        return {
            'locations': [
                {
                    'delivery_information': 'Delivery within 2-4 hours',
                    'keyname': 'TEST00',
                    'long_name': 'Test Data Center'
                },
                {
                    'delivery_information': '',
                    'keyname': 'FIRST_AVAILABLE',
                    'long_name': 'First Available'
                }
            ],
            'categories': {
                'server': {
                    'sort': 0,
                    'step': 0,
                    'is_required': 1,
                    'name': 'Server',
                    'group': 'Key Components',
                    'items': [
                        {
                            'id': 1,
                            'description': 'CPU Core',
                            'sort': 0,
                            'price_id': 1,
                            'recurring_fee': 0.0,
                            'capacity': 0.0,
                        }
                    ],
                },
                'ram': {
                    'sort': 1,
                    'step': 0,
                    'is_required': 1,
                    'name': 'Memory',
                    'group': 'Key Components',
                    'items': [
                        {
                            'id': 21,
                            'description': '2GB',
                            'sort': 0,
                            'price_id': 21,
                            'recurring_fee': 0.0,
                            'capacity': 2,
                        },
                        {
                            'id': 22,
                            'description': '4GB',
                            'sort': 1,
                            'price_id': 22,
                            'recurring_fee': 0.0,
                            'capacity': 4,
                        }
                    ],
                },
                'os': {
                    'sort': 2,
                    'step': 0,
                    'is_required': 1,
                    'name': 'Operating Systems',
                    'group': 'Key Components',
                    'items': [
                        {
                            'id': 31,
                            'description': 'CloudLinux 5 - Minimal Install ' +
                            '(32 bit)',
                            'sort': 0,
                            'price_id': 31,
                            'recurring_fee': 0.0,
                            'capacity': 0.0,
                        },
                        {
                            'id': 32,
                            'description': 'Windows Server 2012 Datacenter' +
                            'Edition With Hyper-V (64bit)',
                            'sort': 0,
                            'price_id': 32,
                            'recurring_fee': 0.0,
                            'capacity': 0.0,
                        },
                        {
                            'id': 33,
                            'description': 'Ubuntu Linux 10.04 LTS Lucid ' +
                            'Lynx (32 bit)',
                            'sort': 0,
                            'price_id': 33,
                            'recurring_fee': 0.0,
                            'capacity': 0.0,
                        }
                    ],
                },
                'disk0': {
                    'sort': 3,
                    'step': 0,
                    'is_required': 1,
                    'name': 'Disk',
                    'group': 'Key Components',
                    'items': [
                        {
                            'id': 4,
                            'description': '100GB SATA',
                            'sort': 0,
                            'price_id': 4,
                            'recurring_fee': 0.0,
                            'capacity': 100.0,
                        }
                    ],
                },
                'disk1': {
                    'sort': 3,
                    'step': 0,
                    'is_required': 1,
                    'name': 'Disk',
                    'group': 'Key Components',
                    'items': [
                        {
                            'id': 4,
                            'description': '100GB SATA',
                            'sort': 0,
                            'price_id': 4,
                            'recurring_fee': 10.0,
                            'capacity': 100.0,
                        }
                    ],
                },
                'port_speed': {
                    'sort': 4,
                    'step': 0,
                    'is_required': 1,
                    'name': 'NIC',
                    'group': 'Key Components',
                    'items': [
                        {
                            'id': 51,
                            'description': '100 Mbps',
                            'sort': 0,
                            'price_id': 51,
                            'recurring_fee': 0.0,
                            'capacity': 100.0,
                        },
                        {
                            'id': 52,
                            'description': '100 Mbps dual',
                            'sort': 0,
                            'price_id': 52,
                            'recurring_fee': 0.0,
                            'capacity': 100.0,
                        }
                    ],
                },
                'disk_controller': {
                    'sort': 5,
                    'step': 0,
                    'is_required': 1,
                    'name': 'Disk Controller',
                    'group': 'Key Components',
                    'items': [
                        {
                            'id': 6,
                            'description': 'RAID 5',
                            'sort': 0,
                            'price_id': 6,
                            'recurring_fee': 0.0,
                            'capacity': 0.0,
                        }
                    ],
                }
            }
        }

    @staticmethod
    def get_server_mocks():
        return [
            {
                'id': 1,
                'datacenter': {'name': 'TEST00',
                               'description': 'Test Data Center'},
                'fullyQualifiedDomainName': 'test1.sftlyr.ws',
                'processorCoreAmount': 2,
                'memoryCapacity': 2,
                'primaryIpAddress': '10.0.0.2',
                'primaryBackendIpAddress': '10.1.0.2',
                'hardwareStatus': {'status': 'ACTIVE'},
                'provisionDate': '2013-08-01 15:23:45',
                'notes': 'These are test notes.',
                'operatingSystem': {
                    'softwareLicense': {
                        'softwareDescription': {
                            'referenceCode': 'Ubuntu',
                            'name': 'Ubuntu 12.04 LTS',
                        }
                    },
                    'passwords': [
                        {'username': 'root', 'password': 'abc123'}
                    ],
                },
                'networkVlans': [
                    {
                        'networkSpace': 'PRIVATE',
                        'vlanNumber': 1800,
                        'id': 9653
                    },
                    {
                        'networkSpace': 'PUBLIC',
                        'vlanNumber': 3672,
                        'id': 19082
                    },
                ]
            },
            {
                'id': 2,
                'datacenter': {'name': 'TEST00',
                               'description': 'Test Data Center'},
                'fullyQualifiedDomainName': 'test2.sftlyr.ws',
                'processorCoreAmount': 4,
                'memoryCapacity': 4,
                'primaryIpAddress': '10.0.0.3',
                'primaryBackendIpAddress': '10.1.0.3',
                'hardwareStatus': {'status': 'ACTIVE'},
                'provisionDate': '2013-08-03 07:15:22',
                'operatingSystem': {
                    'softwareLicense': {
                        'softwareDescription': {
                            'referenceCode': 'Ubuntu',
                            'name': 'Ubuntu 12.04 LTS',
                        }
                    }
                },
                'networkVlans': [
                    {
                        'networkSpace': 'PRIVATE',
                        'vlanNumber': 1800,
                        'id': 9653
                    },
                    {
                        'networkSpace': 'PUBLIC',
                        'vlanNumber': 3672,
                        'id': 19082
                    },
                ]
            }
        ]
