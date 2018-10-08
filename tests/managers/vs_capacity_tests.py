"""
    SoftLayer.tests.managers.vs_capacity_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.

"""
import mock

import SoftLayer
from SoftLayer import fixtures
from SoftLayer.fixtures import SoftLayer_Product_Package
from SoftLayer import testing


class VSCapacityTests(testing.TestCase):

    def set_up(self):
        self.manager = SoftLayer.CapacityManager(self.client)
        amock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        amock.return_value = fixtures.SoftLayer_Product_Package.RESERVED_CAPACITY

    def test_list(self):
        self.manager.list()
        self.assert_called_with('SoftLayer_Account', 'getReservedCapacityGroups')

    def test_get_object(self):
        self.manager.get_object(100)
        self.assert_called_with('SoftLayer_Virtual_ReservedCapacityGroup', 'getObject', identifier=100)

    def test_get_object_mask(self):
        mask = "mask[id]"
        self.manager.get_object(100, mask=mask)
        self.assert_called_with('SoftLayer_Virtual_ReservedCapacityGroup', 'getObject', identifier=100, mask=mask)

    def test_get_create_options(self):
        self.manager.get_create_options()
        self.assert_called_with('SoftLayer_Product_Package', 'getItems', identifier=1059, mask=mock.ANY)

    def test_get_available_routers(self):

        result = self.manager.get_available_routers()
        package_filter = {'keyName': {'operation': 'RESERVED_CAPACITY'}}
        self.assert_called_with('SoftLayer_Product_Package', 'getAllObjects', mask=mock.ANY, filter=package_filter)
        self.assert_called_with('SoftLayer_Product_Package', 'getRegions', mask=mock.ANY)
        self.assert_called_with('SoftLayer_Network_Pod', 'getAllObjects')
        self.assertEqual(result[0]['keyname'], 'WASHINGTON07')

    def test_create(self):
        item_mock = self.set_mock('SoftLayer_Product_Package', 'getItems')
        item_mock.return_value = SoftLayer_Product_Package.getItems_RESERVED_CAPACITY
        self.manager.create(
            name='TEST', backend_router_id=1, flavor='B1_1X2_1_YEAR_TERM', instances=5)

        expected_args = {
            'orderContainers': [
                {
                    'backendRouterId': 1,
                    'name': 'TEST',
                    'packageId': 1059,
                    'location': 0,
                    'quantity': 5,
                    'useHourlyPricing': True,
                    'complexType': 'SoftLayer_Container_Product_Order_Virtual_ReservedCapacity',
                    'prices': [{'id': 217561}
                               ]
                }
            ]
        }

        self.assert_called_with('SoftLayer_Product_Package', 'getAllObjects')
        self.assert_called_with('SoftLayer_Product_Package', 'getItems', identifier=1059)
        self.assert_called_with('SoftLayer_Product_Order', 'placeOrder', args=(expected_args,))

    def test_create_test(self):
        item_mock = self.set_mock('SoftLayer_Product_Package', 'getItems')
        item_mock.return_value = SoftLayer_Product_Package.getItems_RESERVED_CAPACITY
        self.manager.create(
            name='TEST', backend_router_id=1, flavor='B1_1X2_1_YEAR_TERM', instances=5, test=True)

        expected_args = {
            'orderContainers': [
                {
                    'backendRouterId': 1,
                    'name': 'TEST',
                    'packageId': 1059,
                    'location': 0,
                    'quantity': 5,
                    'useHourlyPricing': True,
                    'complexType': 'SoftLayer_Container_Product_Order_Virtual_ReservedCapacity',
                    'prices': [{'id': 217561}],

                }
            ]
        }

        self.assert_called_with('SoftLayer_Product_Package', 'getAllObjects')
        self.assert_called_with('SoftLayer_Product_Package', 'getItems', identifier=1059)
        self.assert_called_with('SoftLayer_Product_Order', 'verifyOrder', args=(expected_args,))

    def test_create_guest(self):
        amock = self.set_mock('SoftLayer_Product_Package', 'getItems')
        amock.return_value = fixtures.SoftLayer_Product_Package.getItems_1_IPV6_ADDRESS
        guest_object = {
            'boot_mode': None,
            'disks': (),
            'domain': 'test.com',
            'hostname': 'A1538172419',
            'hourly': True,
            'ipv6': True,
            'local_disk': None,
            'os_code': 'UBUNTU_LATEST_64',
            'primary_disk': '25',
            'private': False,
            'private_subnet': None,
            'public_subnet': None,
            'ssh_keys': [1234]
        }
        self.manager.create_guest(123, False, guest_object)
        expectedGenerate = {
            'startCpus': None,
            'maxMemory': None,
            'hostname': 'A1538172419',
            'domain': 'test.com',
            'localDiskFlag': None,
            'hourlyBillingFlag': True,
            'supplementalCreateObjectOptions': {
                'bootMode': None,
                'flavorKeyName': 'B1_1X2X25'
            },
            'operatingSystemReferenceCode': 'UBUNTU_LATEST_64',
            'datacenter': {'name': 'dal13'},
            'sshKeys': [{'id': 1234}],
            'localDiskFlag': False
        }

        self.assert_called_with('SoftLayer_Virtual_ReservedCapacityGroup', 'getObject', mask=mock.ANY)
        self.assert_called_with('SoftLayer_Virtual_Guest', 'generateOrderTemplate', args=(expectedGenerate,))
        self.assert_called_with('SoftLayer_Product_Package', 'getAllObjects')
        # id=1059 comes from fixtures.SoftLayer_Product_Order.RESERVED_CAPACITY, production is 859
        self.assert_called_with('SoftLayer_Product_Package', 'getItems', identifier=1059)
        self.assert_called_with('SoftLayer_Product_Order', 'placeOrder')

    def test_create_guest_no_flavor(self):
        guest_object = {
            'boot_mode': None,
            'disks': (),
            'domain': 'test.com',
            'hostname': 'A1538172419',
            'hourly': True,
            'ipv6': True,
            'local_disk': None,
            'os_code': 'UBUNTU_LATEST_64',
            'private': False,
            'private_subnet': None,
            'public_subnet': None,
            'ssh_keys': [1234]
        }
        self.assertRaises(SoftLayer.SoftLayerError, self.manager.create_guest, 123, False, guest_object)

    def test_create_guest_testing(self):
        amock = self.set_mock('SoftLayer_Product_Package', 'getItems')
        amock.return_value = fixtures.SoftLayer_Product_Package.getItems_1_IPV6_ADDRESS
        guest_object = {
            'boot_mode': None,
            'disks': (),
            'domain': 'test.com',
            'hostname': 'A1538172419',
            'hourly': True,
            'ipv6': True,
            'local_disk': None,
            'os_code': 'UBUNTU_LATEST_64',
            'primary_disk': '25',
            'private': False,
            'private_subnet': None,
            'public_subnet': None,
            'ssh_keys': [1234]
        }
        self.manager.create_guest(123, True, guest_object)
        self.assert_called_with('SoftLayer_Product_Order', 'verifyOrder')

    def test_flavor_string(self):
        from SoftLayer.managers.vs_capacity import _flavor_string as _flavor_string
        result = _flavor_string('B1_1X2_1_YEAR_TERM', '25')
        self.assertEqual('B1_1X2X25', result)
