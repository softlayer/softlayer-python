"""
    SoftLayer.tests.CLI.modules.bmc_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This is a series of integration tests designed to test the complete
    command line interface.

    :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
    :license: MIT, see LICENSE for more details.
"""
from SoftLayer.tests import unittest
from mock import MagicMock, patch

from SoftLayer.CLI.helpers import format_output, CLIAbort, ArgumentError
from SoftLayer.CLI.modules import bmc
from SoftLayer.tests.mocks import product_package_mock


class BMCCLITests(unittest.TestCase):
    def setUp(self):
        self.client = self._setup_package_mocks(MagicMock())

    def test_BMCCreateOptions(self):
        args = {
            '--all': True,
            '--datacenter': False,
            '--cpu': False,
            '--nic': False,
            '--disk': False,
            '--os': False,
            '--memory': False,
            '--controller': False,
        }

        output = bmc.BMCCreateOptions(client=self.client).execute(args)

        expected = {
            'datacenter': ['RANDOM_LOCATION'],
            'dual nic': ['1000_DUAL', '100_DUAL', '10_DUAL'],
            'os (CENTOS)': ['CENTOS_6_64_LAMP', 'CENTOS_6_64_MINIMAL'],
            'os (REDHAT)': ['REDHAT_6_64_LAMP', 'REDHAT_6_64_MINIMAL'],
            'os (UBUNTU)': ['UBUNTU_12_64_LAMP', 'UBUNTU_12_64_MINIMAL'],
            'os (WIN)': ['WIN_2008-DC_64', 'WIN_2008-ENT_64',
                         'WIN_2008-STD-R2_64', 'WIN_2008-STD_64',
                         'WIN_2012-DC-HYPERV_64'],
            'disks': [250, 500],
            'single nic': ['100', '1000'],
            'memory/cpu': [
                {'cpu': ['2'], 'memory': '2'},
                {'cpu': ['4'], 'memory': '4'}
            ],
        }

        self.assertEqual(expected, format_output(output, 'python'))

        # Check get_create_options() with invalid input
        self.assertEqual(
            [], bmc.BMCCreateOptions().get_create_options([], 'nope'))

    def test_BMCCreateOptions_with_cpu_only(self):
        args = {
            '--all': False,
            '--datacenter': False,
            '--cpu': True,
            '--nic': False,
            '--disk': False,
            '--os': False,
            '--memory': False,
            '--controller': False,
        }

        output = bmc.BMCCreateOptions(client=self.client).execute(args)

        expected = {
            'memory/cpu': [
                {'cpu': ['2'], 'memory': '2'},
                {'cpu': ['4'], 'memory': '4'}
            ],
        }

        self.assertEqual(expected, format_output(output, 'python'))

    def test_CreateBMCInstance(self):
        args = {
            '--hostname': 'test',
            '--domain': 'example.com',
            '--datacenter': 'TEST00',
            '--cpu': '2',
            '--network': '100',
            '--disk': [250, 250],
            '--os': 'UBUNTU_12_64_MINIMAL',
            '--memory': '2',
            '--controller': False,
            '--test': True,
            '--export': None,
            '--template': None,
            '--hourly': True,
            '--monthly': False,
            '--key': [1234, 456],
            '--vlan_public': 10234,
            '--vlan_private': 20468,
        }

        # First, test the --test flag
        with patch('SoftLayer.HardwareManager.verify_order') as verify_mock:
            verify_mock.return_value = {
                'prices': [
                    {
                        'hourlyRecurringFee': 0.0,
                        'recurringFee': 0.0,
                        'setupFee': 0.0,
                        'item': {'description': 'First Item'},
                    },
                    {
                        'hourlyRecurringFee': 0.50,
                        'recurringFee': 25.0,
                        'setupFee': 0.0,
                        'item': {'description': 'Second Item'},
                    }
                ]
            }
            output = bmc.CreateBMCInstance(client=self.client).execute(args)

            expected = """:...................:......:
:              Item : cost :
:...................:......:
:        First Item : 0.00 :
:       Second Item : 0.50 :
: Total hourly cost : 0.50 :
:...................:......:
 -- ! Prices reflected here are retail and do not take account level discounts and are not guaranteed."""

            self.assertEqual(expected, format_output(output, 'table'))

            args['--hourly'] = False
            args['--monthly'] = True

            output = bmc.CreateBMCInstance(client=self.client).execute(args)

            expected = """:....................:.......:
:               Item :  cost :
:....................:.......:
:         First Item :  0.00 :
:        Second Item : 25.00 :
: Total monthly cost : 25.00 :
:....................:.......:
 -- ! Prices reflected here are retail and do not take account level discounts and are not guaranteed."""

            self.assertEqual(expected, format_output(output, 'table'))

            # Make sure we can order without specifying the disk as well
            args['--disk'] = []

            output = bmc.CreateBMCInstance(client=self.client).execute(args)

            self.assertEqual(expected, format_output(output, 'table'))

            # And make sure we can pass in disk and SSH keys as comma separated
            # strings, which is what templates do
            args['--disk'] = '1000_DRIVE,1000_DRIVE'
            args['--key'] = '123,456'

            output = bmc.CreateBMCInstance(client=self.client).execute(args)

            self.assertEqual(expected, format_output(output, 'table'))

            # Test explicitly setting a RAID configuration
            args['--controller'] = 'RAID0'

            output = bmc.CreateBMCInstance(client=self.client).execute(args)

            self.assertEqual(expected, format_output(output, 'table'))

        # Now test ordering
        with patch('SoftLayer.HardwareManager.place_order') as order_mock:
            order_mock.return_value = {
                'orderId': 98765,
                'orderDate': '2013-08-02 15:23:47'
            }

            args['--test'] = False
            args['--really'] = True

            output = bmc.CreateBMCInstance(client=self.client).execute(args)

            expected = {'id': 98765, 'created': '2013-08-02 15:23:47'}
            self.assertEqual(expected, format_output(output, 'python'))

        # Finally, test cancelling the process
        with patch('SoftLayer.CLI.modules.bmc.confirm') as confirm:
            confirm.return_value = False

            args['--really'] = False

            self.assertRaises(
                CLIAbort,
                bmc.CreateBMCInstance(client=self.client).execute, args)

    def test_CreateBMCInstance_failures(self):
        # This is missing a required argument
        args = {
            '--domain': 'example.com',
            '--datacenter': 'TEST00',
            '--cpu': '2',
            '--network': 100,
            '--disk': [250, 250],
            '--os': 'UBUNTU_12_64_MINIMAL',
            '--memory': '2',
            '--controller': False,
            '--test': True,
            '--export': None,
            '--template': None,
            '--hourly': '0',
            '--monthly': '0',
        }

        runnable = bmc.CreateBMCInstance(client=self.client)

        # Verify that ArgumentError is properly raised on error
        self.assertRaises(ArgumentError, runnable.execute, args)

        # Sending strange values for hourly and monthly
        args['--hostname'] = 'bmc-test'
        self.assertRaises(ArgumentError, runnable.execute, args)

        # Send both hourly and monthly
        args['--hourly'] = True
        args['--monthly'] = True
        self.assertRaises(ArgumentError, runnable.execute, args)

        # Send neither hourly nor monthly
        args['--hourly'] = False
        args['--monthly'] = False
        self.assertRaises(ArgumentError, runnable.execute, args)

        # This is missing a server_core combo
        args['--monthly'] = True
        args['--cpu'] = 100
        self.assertRaises(CLIAbort, runnable.execute, args)

        # This section is missing an OS code
        args['--cpu'] = '2'
        args['--os'] = 'nope'

        self.assertRaises(CLIAbort, runnable.execute, args)

        # This section is missing a NIC speed
        args['--os'] = 'UBUNTU_12_64_MINIMAL'
        args['--network'] = 'nope'

        self.assertRaises(CLIAbort, runnable.execute, args)

    @patch('SoftLayer.CLI.modules.bmc.CLIAbort')
    @patch('SoftLayer.CLI.modules.bmc.no_going_back')
    @patch('SoftLayer.HardwareManager.cancel_metal')
    @patch('SoftLayer.CLI.modules.bmc.resolve_id')
    def test_CancelInstance(
            self, resolve_mock, cancel_mock, ngb_mock, abort_mock):
        hw_id = 12345
        resolve_mock.return_value = hw_id
        ngb_mock.return_value = False

        # Check the positive case
        args = {'--really': True, '--immediate': False}
        bmc.CancelInstance(client=self.client).execute(args)

        cancel_mock.assert_called_with(hw_id, False)

        # Now check to make sure we properly call CLIAbort in the negative case
        args['--really'] = False

        bmc.CancelInstance(client=self.client).execute(args)
        abort_mock.assert_called()

    def test_get_default_value_returns_none_for_unknown_category(self):
        option_mock = {'categories': {'cat1': []}}
        runnable = bmc.CreateBMCInstance(client=self.client)
        output = runnable._get_default_value(option_mock, 'nope')
        self.assertEqual(None, output)

    @staticmethod
    def _setup_package_mocks(client):
        p = client['Product_Package']
        p.getAllObjects = product_package_mock.getAllObjects_Mock()
        p.getConfiguration = product_package_mock.getConfiguration_Mock(True)
        p.getCategories = product_package_mock.getCategories_Mock(True)
        p.getRegions = product_package_mock.getRegions_Mock()

        return client
