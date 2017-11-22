"""
    SoftLayer.tests.CLI.modules.dedicatedhosts_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import json
import mock
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
                             'id': 44701,
                             'memoryCapacity': 242,
                             'name': 'khnguyendh'
                         }]
                         )

    def test_create_options(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = SoftLayer_Product_Package.getAllObjectsDH

        result = self.run_command(['dedicatedhost', 'create-options'])
        self.assert_no_fail(result)

        self.assertEqual(json.loads(result.output), [
            [{"value": "ams01", "datacenter": "Amsterdam 1"},
             {"value": "ams03", "datacenter": "Amsterdam 3"},
             {"value": "dal05", "datacenter": "Dallas 5"},
             {"value": "wdc07", "datacenter": "Washington 7"}], [
                {"dedicated Virtual Host": "56 Cores X 242 RAM X 1.2 TB",
                 "value": 10195}]])

    def test_create(self):
        SoftLayer.CLI.formatting.confirm = mock.Mock()
        SoftLayer.CLI.formatting.confirm.return_value = True
        mock_package_obj = \
            self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock_package_obj.return_value = \
            SoftLayer_Product_Package.getAllObjectsDH
        mock_package_routers = \
            self.set_mock('SoftLayer_Virtual_DedicatedHost',
                          'getAvailableRouters')
        mock_package_routers.return_value = \
            SoftLayer_Virtual_DedicatedHost.getAvailableRouters

        result = self.run_command(['dedicatedhost', 'create',
                                   '--hostname=host',
                                   '--domain=example.com',
                                   '--datacenter=dal05',
                                   '--billing=hourly'])
        self.assert_no_fail(result)

        self.assertEqual(json.loads(result.output),
                         {'created': '2013-08-01 15:23:45', 'id': 1234})

        args = ({
            'useHourlyPricing': True,
            'hardware': [{
                'hostname': u'host',
                'domain': u'example.com',
                'primaryBackendNetworkComponent': {
                    'router': {
                        'id': 51218
                    }
                }
            }],
            'packageId': 813, 'prices': [{'id': 200269}],
            'location': 'DALLAS05',
            'complexType': 'SoftLayer_Container_Product_Order_Virtual_DedicatedHost',
            'quantity': 1},)

        self.assert_called_with('SoftLayer_Product_Order', 'placeOrder',
                                args=args)

    def test_create_verify(self):
        SoftLayer.CLI.formatting.confirm = mock.Mock()
        SoftLayer.CLI.formatting.confirm.return_value = True
        mock_package_obj = \
            self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock_package_obj.return_value = \
            SoftLayer_Product_Package.getAllObjectsDH
        mock_package_routers = \
            self.set_mock('SoftLayer_Virtual_DedicatedHost',
                          'getAvailableRouters')
        mock_package_routers.return_value = \
            SoftLayer_Virtual_DedicatedHost.getAvailableRouters
        mock_package = \
            self.set_mock('SoftLayer_Product_Order', 'verifyOrder')
        mock_package.return_value = \
            SoftLayer_Product_Package.verifyOrderDH

        result = self.run_command(['dedicatedhost', 'create',
                                   '--test',
                                   '--hostname=host',
                                   '--domain=example.com',
                                   '--datacenter=dal05',
                                   '--billing=hourly'])
        self.assert_no_fail(result)

        args = ({
            'useHourlyPricing': True,
            'hardware': [{

                'hostname': 'host',
                'domain': 'example.com',

                'primaryBackendNetworkComponent': {
                    'router': {
                        'id': 51218
                    }
                }
            }],
            'packageId': 813, 'prices': [{'id': 200269}],
            'location': 'DALLAS05',
            'complexType': 'SoftLayer_Container_Product_Order_Virtual_DedicatedHost',
            'quantity': 1},)

        self.assert_called_with('SoftLayer_Product_Order', 'verifyOrder',
                                args=args)

        result = self.run_command(['dedicatedhost', 'create',
                                   '--test',
                                   '--hostname=host',
                                   '--domain=example.com',
                                   '--datacenter=dal05',
                                   '--billing=monthly'])
        self.assert_no_fail(result)

        args = ({
            'useHourlyPricing': True,
            'hardware': [{
                'hostname': 'host',
                'domain': 'example.com',
                'primaryBackendNetworkComponent': {
                    'router': {
                        'id': 51218
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

        result = self.run_command(['dedicatedhost',
                                   'create',
                                   '--hostname=host',
                                   '--domain=example.com',
                                   '--datacenter=dal05',
                                   '--billing=monthly'])
        self.assertEqual(result.exit_code, 2)
        self.assertIsInstance(result.exception, exceptions.CLIAbort)

