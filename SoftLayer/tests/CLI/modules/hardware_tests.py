"""
    SoftLayer.tests.CLI.modules.hardware_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
    :license: BSD, see LICENSE for more details.
"""
try:
    import unittest2 as unittest
except ImportError:
    import unittest  # NOQA
from mock import MagicMock, patch, call

from SoftLayer.CLI.modules.hardware import *


class HardwareCLITests(unittest.TestCase):
    def setUp(self):
        self.client = MagicMock()

    @patch('SoftLayer.HardwareManager.get_cancellation_reasons')
    @patch('SoftLayer.CLI.helpers.Table.add_row')
    def test_HardwareCancelReasons(self, t, reasons):
        test_data = {
            'code1': 'Reason 1',
            'code2': 'Reason 2'
        }
        reasons.return_value = test_data

        HardwareCancelReasons.execute(self.client, {})
        expected = []
        for code, reason in test_data.iteritems():
            expected.append(call([code, reason]))

        t.assert_has_calls(expected)

    @patch('SoftLayer.HardwareManager.get_dedicated_server_create_options')
    @patch('SoftLayer.CLI.modules.hardware.KeyValueTable')
    @patch('SoftLayer.CLI.modules.hardware.Table')
    def test_HardwareCreateOptions(
            self, cpu_table, option_table, create_options):
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

        cpu_table.mock_add_spec(['align', 'add_row'], True)
        option_table.mock_add_spec(['align', 'add_row'], True)

        HardwareCreateOptions.execute(self.client, args)

        cpu_table_expected = [
            call().add_row([1, 'CPU Core'])
        ]
        option_table_expected = [
            call().add_row(['datacenter', ['FIRST_AVAILABLE', 'TEST00']]),
            call().add_row(['memory', [2, 4]]),
            call().add_row(['os (CLOUDLINUX)', ['CLOUDLINUX_5_32']]),
            call().add_row(['os (UBUNTU)', ['UBUNTU_10_32']]),
            call().add_row(['os (WIN)', ['WIN_2012-DC-HYPERV_64']]),
            call().add_row(['disk', ['100_SATA']]),
            call().add_row(['single nic', ['100']]),
            call().add_row(['dual nic', ['100_DUAL']]),
            call().add_row(['disk_controllers', ['RAID5']]),
        ]

        cpu_table.assert_has_calls(cpu_table_expected, any_order=True)
        option_table.assert_has_calls(option_table_expected, any_order=True)

    @patch('SoftLayer.HardwareManager.get_hardware')
    @patch('SoftLayer.CLI.helpers.Table.add_row')
    @patch('SoftLayer.CLI.modules.hardware.FormattedItem')
    @patch('SoftLayer.CLI.modules.hardware.resolve_id')
    @patch('SoftLayer.CLI.modules.hardware.gb')
    def test_HardwareDetails(
            self, gb, resolve_id, formatted_item, t, get_hardware):
        hw_id = 1234

        def resolve_mock(resolver, identifier, name='object'):
            return hw_id

        def formatted_item_mock(short_name, long_name):
            return short_name

        resolve_id.side_effect = resolve_mock
        formatted_item.side_effect = formatted_item_mock
        gb.side_effect = lambda x: x * 1024
        servers = self.get_server_mocks()
        get_hardware.return_value = servers[0]

        HardwareDetails.execute(self.client, {'<identifier>': hw_id})

        expected = [
            call(['id', 1]),
            call(['hostname', 'test1.sftlyr.ws']),
            call(['status', 'ACTIVE']),
            call(['datacenter', 'TEST00']),
            call(['cores', 2]),
            call(['memory', 2048]),
            call(['public_ip', '10.0.0.2']),
            call(['private_ip', '10.1.0.2']),
            call(['os', 'Ubuntu']),
            call(['created', '2013-08-01 15:23:45']),
            call(['notes', 'These are test notes.'])
        ]

        t.assert_has_calls(expected)

    @patch('SoftLayer.HardwareManager.list_hardware')
    @patch('SoftLayer.CLI.helpers.Table.add_row')
    @patch('SoftLayer.CLI.modules.hardware.gb')
    def test_ListHardware(self, gb, t, list_hardware):
        hw_data = self.get_server_mocks()
        list_hardware.return_value = hw_data
        gb.side_effect = lambda x: x * 1024

        ListHardware.execute(self.client, {})
        expected = []
        for server in hw_data:
            expected.append(call([
                server['id'],
                server['datacenter']['name'],
                server['fullyQualifiedDomainName'],
                server['processorCoreAmount'],
                server['memoryCapacity'] * 1024,
                server['primaryIpAddress'],
                server['primaryBackendIpAddress'],
            ]))

        t.assert_has_calls(expected)
        self.assertTrue(gb.called)

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
                            'description': 'CloudLinux 5 (32 bit)',
                            'sort': 0,
                            'price_id': 31,
                            'recurring_fee': 0.0,
                            'capacity': 0.0,
                        },
                        {
                            'id': 32,
                            'description': 'Windows Server 2012 Datacenter ' +
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
                    }
                }
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
            }
        ]
