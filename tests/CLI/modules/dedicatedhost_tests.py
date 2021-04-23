"""
    SoftLayer.tests.CLI.modules.dedicatedhosts_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import json
from unittest import mock as mock

import SoftLayer
from SoftLayer.CLI import exceptions
from SoftLayer.fixtures import SoftLayer_Product_Package
from SoftLayer.fixtures import SoftLayer_Virtual_DedicatedHost
from SoftLayer import testing


class DedicatedHostsTests(testing.TestCase):
    def set_up(self):
        self.dedicated_host = SoftLayer.DedicatedHostManager(self.client)

    def test_list_dedicated_hosts(self):
        result = self.run_command(['dedicatedhost', 'list'])

        self.assert_no_fail(result)
        self.assertEqual(json.loads(result.output),
                         [{
                             'cpuCount': 56,
                             'datacenter': 'dal05',
                             'diskCapacity': 1200,
                             'guestCount': 1,
                             'id': 12345,
                             'memoryCapacity': 242,
                             'name': 'test-dedicated'
                         }]
                         )

    def test_details(self):
        mock = self.set_mock('SoftLayer_Virtual_DedicatedHost', 'getObject')
        mock.return_value = SoftLayer_Virtual_DedicatedHost.getObjectById

        result = self.run_command(['dedicatedhost', 'detail', '12345', '--price', '--guests'])
        self.assert_no_fail(result)

        self.assertEqual(json.loads(result.output),
                         {
                             'cpu count': 56,
                             'create date': '2017-11-02T11:40:56-07:00',
                             'datacenter': 'dal05',
                             'disk capacity': 1200,
                             'guest count': 1,
                             'guests': [{
                                 'domain': 'test.com',
                                 'hostname': 'test-dedicated',
                                 'id': 12345,
                                 'uuid': 'F9329795-4220-4B0A-B970-C86B950667FA'
                             }],
                             'id': 12345,
                             'memory capacity': 242,
                             'modify date': '2017-11-06T11:38:20-06:00',
                             'name': 'test-dedicated',
                             'owner': 'test-dedicated',
                             'price_rate': 1515.556,
                             'router hostname': 'bcr01a.dal05',
                             'router id': 12345}
                         )

    def test_details_no_owner(self):
        mock = self.set_mock('SoftLayer_Virtual_DedicatedHost', 'getObject')
        retVal = SoftLayer_Virtual_DedicatedHost.getObjectById
        retVal['billingItem'] = {}
        mock.return_value = retVal

        result = self.run_command(
            ['dedicatedhost', 'detail', '44701', '--price', '--guests'])
        self.assert_no_fail(result)

        self.assertEqual(json.loads(result.output), {'cpu count': 56,
                                                     'create date': '2017-11-02T11:40:56-07:00',
                                                     'datacenter': 'dal05',
                                                     'disk capacity': 1200,
                                                     'guest count': 1,
                                                     'guests': [{
                                                         'domain': 'test.com',
                                                         'hostname': 'test-dedicated',
                                                         'id': 12345,
                                                         'uuid': 'F9329795-4220-4B0A-B970-C86B950667FA'}],
                                                     'id': 12345,
                                                     'memory capacity': 242,
                                                     'modify date': '2017-11-06T11:38:20-06:00',
                                                     'name': 'test-dedicated',
                                                     'owner': None,
                                                     'price_rate': 0,
                                                     'router hostname': 'bcr01a.dal05',
                                                     'router id': 12345}
                         )

    def test_create_options(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = SoftLayer_Product_Package.getAllObjectsDH

        result = self.run_command(['dh', 'create-options'])
        self.assert_no_fail(result)

        self.assertEqual(json.loads(result.output), [[
            {
                'datacenter': 'Dallas 5',
                'value': 'dal05'
            }],
            [{
                'Dedicated Virtual Host Flavor(s)':
                    '56 Cores X 242 RAM X 1.2 TB',
                'value': '56_CORES_X_242_RAM_X_1_4_TB'
            }
        ]]
        )

    def test_create_options_with_only_datacenter(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = SoftLayer_Product_Package.getAllObjectsDH

        result = self.run_command(['dh', 'create-options', '-d=dal05'])
        self.assertIsInstance(result.exception, exceptions.ArgumentError)

    def test_create_options_get_routers(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = SoftLayer_Product_Package.getAllObjectsDH

        result = self.run_command(['dh',
                                   'create-options',
                                   '--datacenter=dal05',
                                   '--flavor=56_CORES_X_242_RAM_X_1_4_TB'])
        self.assert_no_fail(result)
        self.assertEqual(json.loads(result.output), [[
            {
                'Available Backend Routers': 'bcr01a.dal05'
            },
            {
                'Available Backend Routers': 'bcr02a.dal05'
            },
            {
                'Available Backend Routers': 'bcr03a.dal05'
            },
            {
                'Available Backend Routers': 'bcr04a.dal05'
            }
        ]]
        )

    def test_create(self):
        SoftLayer.CLI.formatting.confirm = mock.Mock()
        SoftLayer.CLI.formatting.confirm.return_value = True
        mock_package_obj = self.set_mock('SoftLayer_Product_Package',
                                         'getAllObjects')
        mock_package_obj.return_value = SoftLayer_Product_Package.getAllObjectsDH

        result = self.run_command(['dedicatedhost', 'create',
                                   '--hostname=test-dedicated',
                                   '--domain=test.com',
                                   '--datacenter=dal05',
                                   '--flavor=56_CORES_X_242_RAM_X_1_4_TB',
                                   '--billing=hourly'])
        self.assert_no_fail(result)
        args = ({
            'hardware': [{
                'domain': 'test.com',
                'primaryBackendNetworkComponent': {
                    'router': {
                        'id': 12345
                    }
                },
                'hostname': 'test-dedicated'
            }],
            'useHourlyPricing': True,
            'location': 'DALLAS05',
            'packageId': 813,
            'complexType': 'SoftLayer_Container_Product_Order_Virtual_DedicatedHost',
            'prices': [{
                        'id': 200269
            }],
            'quantity': 1},)

        self.assert_called_with('SoftLayer_Product_Order', 'placeOrder',
                                args=args)

    def test_create_with_gpu(self):
        SoftLayer.CLI.formatting.confirm = mock.Mock()
        SoftLayer.CLI.formatting.confirm.return_value = True
        mock_package_obj = self.set_mock('SoftLayer_Product_Package',
                                         'getAllObjects')
        mock_package_obj.return_value = SoftLayer_Product_Package.getAllObjectsDHGpu

        result = self.run_command(['dedicatedhost', 'create',
                                   '--hostname=test-dedicated',
                                   '--domain=test.com',
                                   '--datacenter=dal05',
                                   '--flavor=56_CORES_X_484_RAM_X_1_5_TB_X_2_GPU_P100',
                                   '--billing=hourly'])
        self.assert_no_fail(result)
        args = ({
            'hardware': [{
                'domain': 'test.com',
                'primaryBackendNetworkComponent': {
                    'router': {
                        'id': 12345
                    }
                },
                'hostname': 'test-dedicated'
            }],
            'prices': [{
                'id': 200269
            }],
            'location': 'DALLAS05',
            'packageId': 813,
            'complexType': 'SoftLayer_Container_Product_Order_Virtual_DedicatedHost',
            'useHourlyPricing': True,
            'quantity': 1},)

        self.assert_called_with('SoftLayer_Product_Order', 'placeOrder',
                                args=args)

    def test_create_verify(self):
        SoftLayer.CLI.formatting.confirm = mock.Mock()
        SoftLayer.CLI.formatting.confirm.return_value = True
        mock_package_obj = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock_package_obj.return_value = SoftLayer_Product_Package.getAllObjectsDH
        mock_package = self.set_mock('SoftLayer_Product_Order', 'verifyOrder')
        mock_package.return_value = SoftLayer_Product_Package.verifyOrderDH

        result = self.run_command(['dedicatedhost', 'create',
                                   '--verify',
                                   '--hostname=test-dedicated',
                                   '--domain=test.com',
                                   '--datacenter=dal05',
                                   '--flavor=56_CORES_X_242_RAM_X_1_4_TB',
                                   '--billing=hourly'])
        self.assert_no_fail(result)

        args = ({
            'useHourlyPricing': True,
            'hardware': [{

                'hostname': 'test-dedicated',
                'domain': 'test.com',

                'primaryBackendNetworkComponent': {
                    'router': {
                        'id': 12345
                    }
                }
            }],
            'packageId': 813, 'prices': [{'id': 200269}],
            'location': 'DALLAS05',
            'complexType': 'SoftLayer_Container_Product_Order_Virtual_DedicatedHost',
            'quantity': 1},)

        self.assert_called_with('SoftLayer_Product_Order', 'verifyOrder',
                                args=args)

        result = self.run_command(['dh', 'create',
                                   '--verify',
                                   '--hostname=test-dedicated',
                                   '--domain=test.com',
                                   '--datacenter=dal05',
                                   '--flavor=56_CORES_X_242_RAM_X_1_4_TB',
                                   '--billing=monthly'])
        self.assert_no_fail(result)

        args = ({
            'useHourlyPricing': True,
            'hardware': [{
                'hostname': 'test-dedicated',
                'domain': 'test.com',
                'primaryBackendNetworkComponent': {
                            'router': {
                                'id': 12345
                            }
                }
            }],
            'packageId': 813, 'prices': [{'id': 200269}],
            'location': 'DALLAS05',
            'complexType': 'SoftLayer_Container_Product_Order_Virtual_DedicatedHost',
            'quantity': 1},)

        self.assert_called_with('SoftLayer_Product_Order', 'verifyOrder',
                                args=args)

    def test_create_aborted(self):
        SoftLayer.CLI.formatting.confirm = mock.Mock()
        SoftLayer.CLI.formatting.confirm.return_value = False
        mock_package_obj = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock_package_obj.return_value = SoftLayer_Product_Package.getAllObjectsDH

        result = self.run_command(['dh', 'create',
                                   '--hostname=test-dedicated',
                                   '--domain=test.com',
                                   '--datacenter=dal05',
                                   '--flavor=56_CORES_X_242_RAM_X_1_4_TB',
                                   '--billing=monthly'])

        self.assertEqual(result.exit_code, 2)
        self.assertIsInstance(result.exception, exceptions.CLIAbort)

    def test_create_verify_no_price_or_more_than_one(self):
        mock_package_obj = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock_package_obj.return_value = SoftLayer_Product_Package.getAllObjectsDH
        mock_package = self.set_mock('SoftLayer_Product_Order', 'verifyOrder')
        ret_val = SoftLayer_Product_Package.verifyOrderDH
        ret_val['prices'] = []
        mock_package.return_value = ret_val

        result = self.run_command(['dedicatedhost', 'create',
                                   '--verify',
                                   '--hostname=test-dedicated',
                                   '--domain=test.com',
                                   '--datacenter=dal05',
                                   '--flavor=56_CORES_X_242_RAM_X_1_4_TB',
                                   '--billing=hourly'])

        self.assertIsInstance(result.exception, exceptions.ArgumentError)
        args = ({
            'hardware': [{
                'domain': 'test.com',
                'primaryBackendNetworkComponent': {
                    'router': {
                        'id': 12345
                    }
                },
                'hostname': 'test-dedicated'
            }],
            'prices': [{
                'id': 200269
            }],
            'location': 'DALLAS05',
            'packageId': 813,
            'complexType': 'SoftLayer_Container_Product_Order_Virtual_DedicatedHost',
            'useHourlyPricing': True,
            'quantity': 1},)

        self.assert_called_with('SoftLayer_Product_Order', 'verifyOrder', args=args)

    @mock.patch('SoftLayer.DedicatedHostManager.cancel_host')
    def test_cancel_host(self, cancel_mock):
        result = self.run_command(['--really', 'dedicatedhost', 'cancel', '12345'])

        self.assert_no_fail(result)
        cancel_mock.assert_called_with(12345)

        self.assertEqual(str(result.output), 'Dedicated Host 12345 was cancelled\n')

    def test_cancel_host_abort(self):
        result = self.run_command(['dedicatedhost', 'cancel', '12345'])
        self.assertEqual(result.exit_code, 2)
        self.assertIsInstance(result.exception, exceptions.CLIAbort)

    def test_cancel_guests(self):
        vs1 = {'id': 987, 'fullyQualifiedDomainName': 'foobar.example.com'}
        vs2 = {'id': 654, 'fullyQualifiedDomainName': 'wombat.example.com'}
        guests = self.set_mock('SoftLayer_Virtual_DedicatedHost', 'getGuests')
        guests.return_value = [vs1, vs2]

        vs_status1 = {'id': 987, 'server name': 'foobar.example.com', 'status': 'Cancelled'}
        vs_status2 = {'id': 654, 'server name': 'wombat.example.com', 'status': 'Cancelled'}
        expected_result = [vs_status1, vs_status2]

        result = self.run_command(['--really', 'dedicatedhost', 'cancel-guests', '12345'])
        self.assert_no_fail(result)

        self.assertEqual(expected_result, json.loads(result.output))

    def test_cancel_guests_empty_list(self):
        guests = self.set_mock('SoftLayer_Virtual_DedicatedHost', 'getGuests')
        guests.return_value = []

        result = self.run_command(['--really', 'dedicatedhost', 'cancel-guests', '12345'])
        self.assert_no_fail(result)

        self.assertEqual(str(result.output), 'There is not any guest into the dedicated host 12345\n')

    def test_cancel_guests_abort(self):
        result = self.run_command(['dedicatedhost', 'cancel-guests', '12345'])
        self.assertEqual(result.exit_code, 2)

        self.assertIsInstance(result.exception, exceptions.CLIAbort)

    def test_list_guests(self):
        result = self.run_command(['dh', 'list-guests', '123', '--tag=tag'])

        self.assert_no_fail(result)
        self.assertEqual(json.loads(result.output),
                         [{'hostname': 'vs-test1',
                           'domain': 'test.sftlyr.ws',
                           'primary_ip': '172.16.240.2',
                           'id': 200,
                           'power_state': 'Running',
                           'backend_ip': '10.45.19.37'},
                          {'hostname': 'vs-test2',
                           'domain': 'test.sftlyr.ws',
                           'primary_ip': '172.16.240.7',
                           'id': 202,
                           'power_state': 'Running',
                           'backend_ip': '10.45.19.35'}])

    def _get_cancel_guests_return(self):
        vs_status1 = {'id': 123, 'fqdn': 'foobar.example.com', 'status': 'Cancelled'}
        vs_status2 = {'id': 456, 'fqdn': 'wombat.example.com', 'status': 'Cancelled'}
        return [vs_status1, vs_status2]
