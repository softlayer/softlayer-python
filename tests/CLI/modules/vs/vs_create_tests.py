"""
    SoftLayer.tests.CLI.modules.vs.vs_create_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""

import sys
import tempfile
from unittest import mock as mock

from SoftLayer.fixtures import SoftLayer_Product_Package as SoftLayer_Product_Package
from SoftLayer import testing


class VirtCreateTests(testing.TestCase):

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_create(self, confirm_mock):
        confirm_mock.return_value = True
        result = self.run_command(['vs', 'create',
                                   '--cpu=2',
                                   '--domain=example.com',
                                   '--hostname=host',
                                   '--os=UBUNTU_LATEST',
                                   '--memory=1',
                                   '--network=100',
                                   '--billing=hourly',
                                   '--datacenter=dal05',
                                   '--tag=dev',
                                   '--tag=green'])

        self.assert_no_fail(result)
        self.assertIn('"guid": "1a2b3c-1701"', result.output)
        self.assert_called_with('SoftLayer_Product_Order', 'placeOrder')

        args = ({'datacenter': {'name': 'dal05'},
                 'domain': 'example.com',
                 'hourlyBillingFlag': True,
                 'localDiskFlag': True,
                 'maxMemory': 1024,
                 'hostname': 'host',
                 'startCpus': 2,
                 'operatingSystemReferenceCode': 'UBUNTU_LATEST',
                 'networkComponents': [{'maxSpeed': 100}],
                 'supplementalCreateObjectOptions': {'bootMode': None}},)
        self.assert_called_with('SoftLayer_Virtual_Guest', 'generateOrderTemplate', args=args)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_create_vlan_subnet(self, confirm_mock):
        confirm_mock.return_value = True

        result = self.run_command(['vs', 'create',
                                   '--cpu=2',
                                   '--domain=example.com',
                                   '--hostname=host',
                                   '--os=UBUNTU_LATEST',
                                   '--memory=1',
                                   '--billing=hourly',
                                   '--datacenter=dal05',
                                   '--vlan-private=577940',
                                   '--subnet-private=478700',
                                   '--vlan-public=1639255',
                                   '--subnet-public=297614',
                                   '--tag=dev',
                                   '--tag=green'])

        self.assert_no_fail(result)
        self.assertIn('"guid": "1a2b3c-1701"', result.output)
        self.assert_called_with('SoftLayer_Product_Order', 'placeOrder')
        args = ({
            'startCpus': 2,
            'maxMemory': 1024,
            'hostname': 'host',
            'domain': 'example.com',
            'localDiskFlag': True,
            'hourlyBillingFlag': True,
            'supplementalCreateObjectOptions': {'bootMode': None},
            'operatingSystemReferenceCode': 'UBUNTU_LATEST',
            'datacenter': {'name': 'dal05'},
            'primaryBackendNetworkComponent': {
                'networkVlan': {
                    'id': 577940,
                    'primarySubnet': {'id': 478700}
                }
            },
            'primaryNetworkComponent': {
                'networkVlan': {
                    'id': 1639255,
                    'primarySubnet': {'id': 297614}
                }
            }
        },)

        self.assert_called_with('SoftLayer_Virtual_Guest', 'generateOrderTemplate', args=args)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_create_by_router(self, confirm_mock):
        confirm_mock.return_value = True

        result = self.run_command(['vs', 'create',
                                   '--cpu=2',
                                   '--domain=example.com',
                                   '--hostname=host',
                                   '--os=UBUNTU_LATEST',
                                   '--memory=1',
                                   '--billing=hourly',
                                   '--datacenter=dal05',
                                   '--router-private=577940',
                                   '--router-public=1639255',
                                   '--tag=dev',
                                   '--tag=green'])

        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Product_Order', 'placeOrder')
        args = ({
            'startCpus': 2,
            'maxMemory': 1024,
            'hostname': 'host',
            'domain': 'example.com',
            'localDiskFlag': True,
            'hourlyBillingFlag': True,
            'supplementalCreateObjectOptions': {'bootMode': None},
            'operatingSystemReferenceCode': 'UBUNTU_LATEST',
            'datacenter': {'name': 'dal05'},
            'primaryBackendNetworkComponent': {
                        'router': {
                            'id': 577940
                        }
            },
            'primaryNetworkComponent': {
                'router': {
                    'id': 1639255
                }
            }
        },)

        self.assert_called_with('SoftLayer_Virtual_Guest', 'generateOrderTemplate', args=args)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_create_with_wait_ready(self, confirm_mock):
        mock = self.set_mock('SoftLayer_Virtual_Guest', 'getObject')
        mock.return_value = {
            "provisionDate": "2018-06-10T12:00:00-05:00",
            "id": 100
        }
        confirm_mock.return_value = True

        result = self.run_command(['vs', 'create',
                                   '--cpu=2',
                                   '--domain=example.com',
                                   '--hostname=host',
                                   '--os=UBUNTU_LATEST',
                                   '--memory=1',
                                   '--network=100',
                                   '--billing=hourly',
                                   '--datacenter=dal05',
                                   '--wait=1'])

        self.assert_no_fail(result)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_create_with_wait_not_ready(self, confirm_mock):
        mock = self.set_mock('SoftLayer_Virtual_Guest', 'getObject')
        mock.return_value = {
            "ready": False,
            "guid": "1a2b3c-1701",
            "id": 100,
            "created": "2018-06-10 12:00:00"
        }
        confirm_mock.return_value = True

        result = self.run_command(['vs', 'create',
                                   '--cpu=2',
                                   '--domain=example.com',
                                   '--hostname=host',
                                   '--os=UBUNTU_LATEST',
                                   '--memory=1',
                                   '--network=100',
                                   '--billing=hourly',
                                   '--datacenter=dal05',
                                   '--wait=1'])

        self.assertEqual(result.exit_code, 1)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_create_with_integer_image_id(self, confirm_mock):
        confirm_mock.return_value = True
        result = self.run_command(['vs', 'create',
                                   '--cpu=2',
                                   '--domain=example.com',
                                   '--hostname=host',
                                   '--image=12345',
                                   '--memory=1',
                                   '--network=100',
                                   '--billing=hourly',
                                   '--datacenter=dal05'])

        self.assert_no_fail(result)
        self.assertIn('"guid": "1a2b3c-1701"', result.output)
        self.assert_called_with('SoftLayer_Product_Order', 'placeOrder')

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_create_with_integer_image_guid(self, confirm_mock):
        confirm_mock.return_value = True
        result = self.run_command(['vs', 'create',
                                   '--cpu=2',
                                   '--domain=example.com',
                                   '--hostname=host',
                                   '--image=aaaa1111bbbb2222',
                                   '--memory=1',
                                   '--network=100',
                                   '--billing=hourly',
                                   '--datacenter=dal05'])

        self.assert_no_fail(result)
        self.assertIn('"guid": "1a2b3c-1701"', result.output)
        args = ({
            'startCpus': 2,
            'maxMemory': 1024,
            'hostname': 'host',
            'domain': 'example.com',
            'localDiskFlag': True,
            'hourlyBillingFlag': True,
            'supplementalCreateObjectOptions': {'bootMode': None},
            'blockDeviceTemplateGroup': {'globalIdentifier': 'aaaa1111bbbb2222'},
            'datacenter': {'name': 'dal05'},
            'networkComponents': [{'maxSpeed': 100}]
        },)

        self.assert_called_with('SoftLayer_Virtual_Guest', 'generateOrderTemplate', args=args)
        self.assert_called_with('SoftLayer_Product_Order', 'placeOrder')

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_create_with_flavor(self, confirm_mock):
        confirm_mock.return_value = True
        result = self.run_command(['vs', 'create',
                                   '--domain=example.com',
                                   '--hostname=host',
                                   '--os=UBUNTU_LATEST',
                                   '--network=100',
                                   '--billing=hourly',
                                   '--datacenter=dal05',
                                   '--flavor=B1_1X2X25'])

        self.assert_no_fail(result)
        self.assertIn('"guid": "1a2b3c-1701"', result.output)
        self.assert_called_with('SoftLayer_Product_Order', 'placeOrder')
        args = ({'datacenter': {'name': 'dal05'},
                 'domain': 'example.com',
                 'hourlyBillingFlag': True,
                 'hostname': 'host',
                 'startCpus': None,
                 'maxMemory': None,
                 'localDiskFlag': None,
                 'supplementalCreateObjectOptions': {
                     'bootMode': None,
                     'flavorKeyName': 'B1_1X2X25'},
                 'operatingSystemReferenceCode': 'UBUNTU_LATEST',
                 'networkComponents': [{'maxSpeed': 100}]},)

        self.assert_called_with('SoftLayer_Virtual_Guest', 'generateOrderTemplate', args=args)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_create_with_flavor_and_memory(self, confirm_mock):
        confirm_mock.return_value = True

        result = self.run_command(['vs', 'create',
                                   '--domain=example.com',
                                   '--hostname=host',
                                   '--os=UBUNTU_LATEST',
                                   '--network=100',
                                   '--datacenter=TEST00',
                                   '--flavor=BL_1X2X25',
                                   '--memory=2048MB'])

        self.assertEqual(result.exit_code, 2)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_create_with_dedicated_and_flavor(self, confirm_mock):
        confirm_mock.return_value = True

        result = self.run_command(['vs', 'create',
                                   '--domain=example.com',
                                   '--hostname=host',
                                   '--os=UBUNTU_LATEST',
                                   '--network=100',
                                   '--datacenter=TEST00',
                                   '--dedicated',
                                   '--flavor=BL_1X2X25'])

        self.assertEqual(result.exit_code, 2)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_create_with_hostid_and_flavor(self, confirm_mock):
        confirm_mock.return_value = True

        result = self.run_command(['vs', 'create',
                                   '--domain=example.com',
                                   '--hostname=host',
                                   '--os=UBUNTU_LATEST',
                                   '--network=100',
                                   '--datacenter=dal05',
                                   '--host-id=100',
                                   '--flavor=BL_1X2X25'])

        self.assertEqual(result.exit_code, 2)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_create_with_flavor_and_cpu(self, confirm_mock):
        confirm_mock.return_value = True

        result = self.run_command(['vs', 'create',
                                   '--domain=example.com',
                                   '--hostname=host',
                                   '--os=UBUNTU_LATEST',
                                   '--network=100',
                                   '--datacenter=TEST00',
                                   '--flavor=BL_1X2X25',
                                   '--cpu=2'])

        self.assertEqual(result.exit_code, 2)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_create_with_host_id(self, confirm_mock):
        confirm_mock.return_value = True
        result = self.run_command(['vs', 'create',
                                   '--cpu=2',
                                   '--domain=example.com',
                                   '--hostname=host',
                                   '--os=UBUNTU_LATEST',
                                   '--memory=1',
                                   '--network=100',
                                   '--billing=hourly',
                                   '--datacenter=dal05',
                                   '--dedicated',
                                   '--host-id=123'])

        self.assert_no_fail(result)
        self.assertIn('"guid": "1a2b3c-1701"', result.output)
        # Argument testing Example
        order_call = self.calls('SoftLayer_Product_Order', 'placeOrder')
        order_args = getattr(order_call[0], 'args')[0]
        self.assertEqual(123, order_args['hostId'])

        self.assert_called_with('SoftLayer_Product_Order', 'placeOrder')
        template_args = ({
            'startCpus': 2,
            'maxMemory': 1024,
            'hostname': 'host',
            'domain': 'example.com',
            'localDiskFlag': True,
            'hourlyBillingFlag': True,
            'supplementalCreateObjectOptions': {'bootMode': None},
            'dedicatedHost': {'id': 123},
            'operatingSystemReferenceCode': 'UBUNTU_LATEST',
            'datacenter': {'name': 'dal05'},
            'networkComponents': [{'maxSpeed': 100}]
        },)

        self.assert_called_with('SoftLayer_Virtual_Guest', 'generateOrderTemplate', args=template_args)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_create_like(self, confirm_mock):
        mock = self.set_mock('SoftLayer_Virtual_Guest', 'getObject')
        mock.return_value = {
            'hostname': 'vs-test-like',
            'domain': 'test.sftlyr.ws',
            'maxCpu': 2,
            'maxMemory': 1024,
            'datacenter': {'name': 'dal05'},
            'networkComponents': [{'maxSpeed': 100}],
            'dedicatedAccountHostOnlyFlag': False,
            'privateNetworkOnlyFlag': False,
            'billingItem': {'orderItem': {'preset': {}}},
            'operatingSystem': {'softwareLicense': {
                'softwareDescription': {'referenceCode': 'UBUNTU_LATEST'}
            }},
            'hourlyBillingFlag': False,
            'localDiskFlag': True,
            'userData': {}
        }

        confirm_mock.return_value = True
        result = self.run_command(['vs', 'create',
                                   '--like=123',
                                   '--san',
                                   '--billing=hourly'])

        self.assert_no_fail(result)
        self.assertIn('"guid": "1a2b3c-1701"', result.output)
        self.assert_called_with('SoftLayer_Product_Order', 'placeOrder')

        args = ({'datacenter': {'name': 'dal05'},
                 'domain': 'test.sftlyr.ws',
                 'hourlyBillingFlag': True,
                 'hostname': 'vs-test-like',
                 'startCpus': 2,
                 'maxMemory': 1024,
                 'localDiskFlag': False,
                 'operatingSystemReferenceCode': 'UBUNTU_LATEST',
                 'networkComponents': [{'maxSpeed': 100}],
                 'supplementalCreateObjectOptions': {'bootMode': None}},)
        self.assert_called_with('SoftLayer_Virtual_Guest', 'generateOrderTemplate', args=args)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_create_like_tags(self, confirm_mock):
        mock = self.set_mock('SoftLayer_Virtual_Guest', 'getObject')
        mock.return_value = {
            'hostname': 'vs-test-like',
            'domain': 'test.sftlyr.ws',
            'maxCpu': 2,
            'maxMemory': 1024,
            'datacenter': {'name': 'dal05'},
            'networkComponents': [{'maxSpeed': 100}],
            'dedicatedAccountHostOnlyFlag': False,
            'privateNetworkOnlyFlag': False,
            'billingItem': {'orderItem': {'preset': {}}},
            'operatingSystem': {'softwareLicense': {
                'softwareDescription': {'referenceCode': 'UBUNTU_LATEST'}
            }},
            'hourlyBillingFlag': False,
            'localDiskFlag': True,
            'userData': {},
            'tagReferences': [{'tag': {'name': 'production'}}],
        }

        confirm_mock.return_value = True
        result = self.run_command(['vs', 'create',
                                   '--like=123',
                                   '--san',
                                   '--billing=hourly'])

        self.assert_no_fail(result)
        self.assertIn('"guid": "1a2b3c-1701"', result.output)
        self.assert_called_with('SoftLayer_Product_Order', 'placeOrder')
        _args = ('production',)
        self.assert_called_with('SoftLayer_Virtual_Guest', 'setTags', identifier=1234567, args=_args)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_create_like_image(self, confirm_mock):
        mock = self.set_mock('SoftLayer_Virtual_Guest', 'getObject')
        mock.return_value = {
            'hostname': 'vs-test-like',
            'domain': 'test.sftlyr.ws',
            'maxCpu': 2,
            'maxMemory': 1024,
            'datacenter': {'name': 'dal05'},
            'networkComponents': [{'maxSpeed': 100}],
            'dedicatedAccountHostOnlyFlag': False,
            'privateNetworkOnlyFlag': False,
            'billingItem': {'orderItem': {'preset': {}}},
            'blockDeviceTemplateGroup': {'globalIdentifier': 'aaa1xxx1122233'},
            'hourlyBillingFlag': False,
            'localDiskFlag': True,
            'userData': {},
        }

        confirm_mock.return_value = True
        result = self.run_command(['vs', 'create',
                                   '--like=123',
                                   '--san',
                                   '--billing=hourly'])

        self.assert_no_fail(result)
        self.assertIn('"guid": "1a2b3c-1701"', result.output)
        self.assert_called_with('SoftLayer_Product_Order', 'placeOrder')
        args = ({'datacenter': {'name': 'dal05'},
                 'domain': 'test.sftlyr.ws',
                 'hourlyBillingFlag': True,
                 'hostname': 'vs-test-like',
                 'startCpus': 2,
                 'maxMemory': 1024,
                 'localDiskFlag': False,
                 'blockDeviceTemplateGroup': {'globalIdentifier': 'aaa1xxx1122233'},
                 'networkComponents': [{'maxSpeed': 100}],
                 'supplementalCreateObjectOptions': {'bootMode': None}},)
        self.assert_called_with('SoftLayer_Virtual_Guest', 'generateOrderTemplate', args=args)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_create_like_flavor(self, confirm_mock):
        mock = self.set_mock('SoftLayer_Virtual_Guest', 'getObject')
        mock.return_value = {
            'hostname': 'vs-test-like',
            'domain': 'test.sftlyr.ws',
            'maxCpu': 2,
            'maxMemory': 1024,
            'datacenter': {'name': 'dal05'},
            'networkComponents': [{'maxSpeed': 100}],
            'dedicatedAccountHostOnlyFlag': False,
            'privateNetworkOnlyFlag': False,
            'billingItem': {'orderItem': {'preset': {'keyName': 'B1_1X2X25'}}},
            'operatingSystem': {'softwareLicense': {
                'softwareDescription': {'referenceCode': 'UBUNTU_LATEST'}
            }},
            'hourlyBillingFlag': True,
            'localDiskFlag': False,
            'userData': {}
        }

        confirm_mock.return_value = True
        result = self.run_command(['vs', 'create', '--like=123'])

        self.assert_no_fail(result)
        self.assertIn('"guid": "1a2b3c-1701"', result.output)
        self.assert_called_with('SoftLayer_Product_Order', 'placeOrder')

        args = ({'datacenter': {'name': 'dal05'},
                 'domain': 'test.sftlyr.ws',
                 'hourlyBillingFlag': True,
                 'hostname': 'vs-test-like',
                 'startCpus': None,
                 'maxMemory': None,
                 'localDiskFlag': None,
                 'supplementalCreateObjectOptions': {
                     'bootMode': None,
                     'flavorKeyName': 'B1_1X2X25'},
                 'operatingSystemReferenceCode': 'UBUNTU_LATEST',
                 'networkComponents': [{'maxSpeed': 100}]},)
        self.assert_called_with('SoftLayer_Virtual_Guest', 'generateOrderTemplate', args=args)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_create_like_transient(self, confirm_mock):
        mock = self.set_mock('SoftLayer_Virtual_Guest', 'getObject')
        mock.return_value = {
            'hostname': 'vs-test-like',
            'domain': 'test.sftlyr.ws',
            'datacenter': {'name': 'dal05'},
            'networkComponents': [{'maxSpeed': 100}],
            'dedicatedAccountHostOnlyFlag': False,
            'privateNetworkOnlyFlag': False,
            'billingItem': {'orderItem': {'preset': {'keyName': 'B1_1X2X25'}}},
            'operatingSystem': {'softwareLicense': {
                'softwareDescription': {'referenceCode': 'UBUNTU_LATEST'}
            }},
            'hourlyBillingFlag': True,
            'localDiskFlag': False,
            'transientGuestFlag': True,
            'userData': {}
        }

        confirm_mock.return_value = True
        result = self.run_command(['vs', 'create', '--like=123'])

        self.assert_no_fail(result)
        self.assertIn('"guid": "1a2b3c-1701"', result.output)
        self.assert_called_with('SoftLayer_Product_Order', 'placeOrder')

        args = ({'datacenter': {'name': 'dal05'},
                 'domain': 'test.sftlyr.ws',
                 'hourlyBillingFlag': True,
                 'hostname': 'vs-test-like',
                 'startCpus': None,
                 'maxMemory': None,
                 'localDiskFlag': None,
                 'transientGuestFlag': True,
                 'supplementalCreateObjectOptions': {
                     'bootMode': None,
                     'flavorKeyName': 'B1_1X2X25'},
                 'operatingSystemReferenceCode': 'UBUNTU_LATEST',
                 'networkComponents': [{'maxSpeed': 100}]},)
        self.assert_called_with('SoftLayer_Virtual_Guest', 'generateOrderTemplate', args=args)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_create_vs_test(self, confirm_mock):
        confirm_mock.return_value = True

        result = self.run_command(['vs', 'create', '--test', '--hostname', 'TEST',
                                   '--domain', 'TESTING', '--cpu', '1',
                                   '--memory', '2048MB', '--datacenter',
                                   'TEST00', '--os', 'UBUNTU_LATEST'])

        self.assertEqual(result.exit_code, 0)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_create_vs_flavor_test(self, confirm_mock):
        confirm_mock.return_value = True

        result = self.run_command(['vs', 'create', '--test', '--hostname', 'TEST',
                                   '--domain', 'TESTING', '--flavor', 'B1_2X8X25',
                                   '--datacenter', 'TEST00', '--os', 'UBUNTU_LATEST'])

        self.assert_no_fail(result)
        self.assertEqual(result.exit_code, 0)

    def test_create_vs_bad_memory(self):
        result = self.run_command(['vs', 'create', '--hostname', 'TEST',
                                   '--domain', 'TESTING', '--cpu', '1',
                                   '--memory', '2034MB', '--flavor',
                                   'B1_2X8X25', '--datacenter', 'TEST00'])

        self.assertEqual(2, result.exit_code)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_create_vs_transient(self, confirm_mock):
        confirm_mock.return_value = True

        result = self.run_command(['vs', 'create', '--hostname', 'TEST',
                                   '--domain', 'TESTING', '--flavor',
                                   'B1_2X8X25', '--datacenter', 'TEST00',
                                   '--transient', '--os', 'UBUNTU_LATEST'])

        self.assert_no_fail(result)
        self.assertEqual(0, result.exit_code)

    def test_create_vs_bad_transient_monthly(self):
        result = self.run_command(['vs', 'create', '--hostname', 'TEST',
                                   '--domain', 'TESTING', '--flavor',
                                   'B1_2X8X25', '--datacenter', 'TEST00',
                                   '--transient', '--billing', 'monthly',
                                   '--os', 'UBUNTU_LATEST'])

        self.assertEqual(2, result.exit_code)

    def test_create_vs_bad_transient_dedicated(self):
        result = self.run_command(['vs', 'create', '--hostname', 'TEST',
                                   '--domain', 'TESTING', '--flavor',
                                   'B1_2X8X25', '--datacenter', 'TEST00',
                                   '--transient', '--dedicated',
                                   '--os', 'UBUNTU_LATEST'])

        self.assertEqual(2, result.exit_code)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_create_with_ipv6(self, confirm_mock):
        amock = self.set_mock('SoftLayer_Product_Package', 'getItems')
        amock.return_value = SoftLayer_Product_Package.getItems_1_IPV6_ADDRESS
        result = self.run_command(['vs', 'create', '--test', '--hostname', 'TEST',
                                   '--domain', 'TESTING', '--flavor', 'B1_2X8X25',
                                   '--datacenter', 'TEST00', '--os', 'UBUNTU_LATEST', '--ipv6'])

        self.assert_no_fail(result)
        self.assertEqual(result.exit_code, 0)
        self.assert_called_with('SoftLayer_Product_Order', 'verifyOrder')
        args = ({
            'startCpus': None,
            'maxMemory': None,
            'hostname': 'TEST',
            'domain': 'TESTING',
            'localDiskFlag': None,
            'hourlyBillingFlag': True,
            'supplementalCreateObjectOptions': {
                'bootMode': None,
                'flavorKeyName': 'B1_2X8X25'
            },
            'operatingSystemReferenceCode': 'UBUNTU_LATEST',
            'datacenter': {
                'name': 'TEST00'
            }
        },
        )
        self.assert_called_with('SoftLayer_Virtual_Guest', 'generateOrderTemplate', args=args)
        self.assertEqual([], self.calls('SoftLayer_Virtual_Guest', 'setTags'))

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_create_with_ipv6_no_test(self, confirm_mock):
        confirm_mock.return_value = True
        amock = self.set_mock('SoftLayer_Product_Package', 'getItems')
        amock.return_value = SoftLayer_Product_Package.getItems_1_IPV6_ADDRESS
        result = self.run_command(['vs', 'create', '--hostname', 'TEST',
                                   '--domain', 'TESTING', '--flavor', 'B1_2X8X25',
                                   '--datacenter', 'TEST00', '--os', 'UBUNTU_LATEST', '--ipv6'])

        self.assert_no_fail(result)
        self.assertEqual(result.exit_code, 0)
        self.assert_called_with('SoftLayer_Product_Order', 'placeOrder')
        self.assertEqual([], self.calls('SoftLayer_Virtual_Guest', 'setTags'))

    @mock.patch('SoftLayer.CLI.formatting.no_going_back')
    def test_create_with_ipv6_no_prices(self, confirm_mock):
        """Test makes sure create fails if ipv6 price cannot be found.

        Since its hard to test if the price ids gets added to placeOrder call,
        this test juse makes sure that code block isn't being skipped
        """
        confirm_mock.return_value = True
        amock = self.set_mock('SoftLayer_Product_Package', 'getItems')
        amock.return_value = SoftLayer_Product_Package.getItemsVS
        result = self.run_command(['vs', 'create', '--test', '--hostname', 'TEST',
                                   '--domain', 'TESTING', '--flavor', 'B1_2X8X25',
                                   '--datacenter', 'TEST00', '--os', 'UBUNTU_LATEST',
                                   '--ipv6'])
        self.assertEqual(result.exit_code, 1)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_create_vs_no_confirm(self, confirm_mock):
        confirm_mock.return_value = False

        result = self.run_command(['vs', 'create', '--hostname', 'TEST',
                                   '--domain', 'TESTING', '--flavor', 'B1_2X8X25',
                                   '--datacenter', 'TEST00', '--os', 'UBUNTU_LATEST'])

        self.assertEqual(result.exit_code, 2)

    def test_create_vs_export(self):
        if(sys.platform.startswith("win")):
            self.skipTest("Test doesn't work in Windows")
        with tempfile.NamedTemporaryFile() as config_file:
            result = self.run_command(['vs', 'create', '--hostname', 'TEST', '--export', config_file.name,
                                       '--domain', 'TESTING', '--flavor', 'B1_2X8X25',
                                       '--datacenter', 'TEST00', '--os', 'UBUNTU_LATEST'])
            self.assert_no_fail(result)
            self.assertIn('Successfully exported options to a template file.', result.output)
            contents = config_file.read().decode("utf-8")
            self.assertIn('hostname=TEST', contents)
            self.assertIn('flavor=B1_2X8X25', contents)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_create_with_userdata(self, confirm_mock):
        result = self.run_command(['vs', 'create', '--hostname', 'TEST', '--domain', 'TESTING',
                                   '--flavor', 'B1_2X8X25', '--datacenter', 'TEST00', '--os', 'UBUNTU_LATEST',
                                   '--userdata', 'This is my user data ok'])
        self.assert_no_fail(result)
        expected_guest = [
            {
                'domain': 'test.local',
                'hostname': 'test',
                'userData': [{'value': 'This is my user data ok'}]
            }
        ]
        # Returns a list of API calls that hit SL_Product_Order::placeOrder
        api_call = self.calls('SoftLayer_Product_Order', 'placeOrder')
        # Doing this because the placeOrder args are huge and mostly not needed to test
        self.assertEqual(api_call[0].args[0]['virtualGuests'], expected_guest)
