"""
    SoftLayer.tests.CLI.modules.hardware_tests
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
from mock import MagicMock, patch, call

from SoftLayer.CLI.helpers import format_output
from SoftLayer.CLI.modules.hardware import *


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

        output = HardwareCancelReasons.execute(self.client, {})

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

        output = HardwareCreateOptions.execute(self.client, args)

        expected = {
            'datacenter': ['FIRST_AVAILABLE', 'TEST00'],
            'dual nic': ['100_DUAL'],
            'disk_controllers': ['RAID5'],
            'os (CLOUDLINUX)': ['CLOUDLINUX_5_32'],
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

        output = HardwareDetails.execute(self.client, {'<identifier>': hw_id})

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
            'vlans': [],
            'os':
            'Ubuntu', 'id': 1,
            'vlans': [{'id': 9653, 'number': 1800, 'type': 'PRIVATE'},
                      {'id': 19082, 'number': 3672, 'type': 'PUBLIC'}]
        }

        self.assertEqual(expected, format_output(output, 'python'))

    @patch('SoftLayer.HardwareManager.list_hardware')
    def test_ListHardware(self, list_hardware):
        hw_data = self.get_server_mocks()
        list_hardware.return_value = hw_data

        output = ListHardware.execute(self.client, {'--tags': 'openstack'})

        expected = [
            {
                'datacenter': 'TEST00',
                'primary_ip': '10.0.0.2',
                'host': 'test1.sftlyr.ws',
                'memory': 2048,
                'cores': 2,
                'id': 1,
                'backend_ip': '10.1.0.2'
            },
            {
                'datacenter': 'TEST00',
                'primary_ip': '10.0.0.3',
                'host': 'test2.sftlyr.ws',
                'memory': 4096,
                'cores': 4,
                'id': 2,
                'backend_ip': '10.1.0.3'
            }
        ]

        self.assertEqual(expected, format_output(output, 'python'))

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
