"""
    SoftLayer.tests.managers.dedicated_host_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import mock
import SoftLayer

from SoftLayer import exceptions
from SoftLayer import fixtures
from SoftLayer import testing


class DedicatedHostTests(testing.TestCase):
    def set_up(self):
        self.dedicated_host = SoftLayer.DedicatedHostManager(self.client)

    def test_list_instances(self):
        results = self.dedicated_host.list_instances()

        self.assertEqual(results, fixtures.SoftLayer_Account.getDedicatedHosts)
        self.assert_called_with('SoftLayer_Account', 'getDedicatedHosts')

    def test_list_instances_with_filters(self):
        results = self.dedicated_host.list_instances(
            tags=['tag1', 'tag2'],
            cpus=2,
            memory=1,
            hostname='hostname',
            datacenter='dal05',
            disk=1
        )
        self.assertEqual(results, fixtures.SoftLayer_Account.getDedicatedHosts)

    def test_get_host(self):

        self.dedicated_host.host = mock.Mock()
        self.dedicated_host.host.getObject.return_value = 'test'

        self.dedicated_host.get_host(12345)

        mask = (
            'id,'
            'name,'
            'cpuCount,'
            'memoryCapacity,'
            'diskCapacity,'
            'createDate,'
            'modifyDate,'
            'backendRouter[id, hostname, domain],'
            'billingItem[id, nextInvoiceTotalRecurringAmount, '
            'children[categoryCode,nextInvoiceTotalRecurringAmount],'
            'orderItem[id, order.userRecord[username]]],'
            'datacenter[id, name, longName],'
            'guests[id, hostname, domain, uuid],'
            'guestCount'
        )
        self.dedicated_host.host.getObject.assert_called_once_with(id=12345, mask=mask)

    def test_place_order(self):
        create_dict = self.dedicated_host._generate_create_dict = mock.Mock()

        values = {
            'hardware': [
                {
                    'primaryBackendNetworkComponent': {
                        'router': {
                            'id': 51218
                        }
                    },
                    'domain': u'test.com',
                    'hostname': u'test'
                }
            ],
            'useHourlyPricing': True,
            'location': 'AMSTERDAM',
            'packageId': 813,
            'complexType': 'SoftLayer_Container_Product_Order_Virtual_DedicatedHost',
            'prices': [
                {
                    'id': 200269
                }
            ],
            'quantity': 1
        }
        create_dict.return_value = values

        location = 'ams01'
        hostname = 'test'
        domain = 'test.com'
        hourly = True

        self.dedicated_host.place_order(hostname=hostname,
                                        domain=domain,
                                        location=location,
                                        hourly=hourly)

        create_dict.assert_called_once_with(hostname=hostname,
                                            router=None,
                                            domain=domain,
                                            datacenter=location,
                                            hourly=True)

        self.assert_called_with('SoftLayer_Product_Order',
                                'placeOrder',
                                args=(values,))

    def test_verify_order(self):
        create_dict = self.dedicated_host._generate_create_dict = mock.Mock()

        values = {
            'hardware': [
                {
                    'primaryBackendNetworkComponent': {
                        'router': {
                            'id': 51218
                        }
                    },
                    'domain': u'test.com',
                    'hostname': u'test'
                }
            ],
            'useHourlyPricing': True,
            'location': 'AMSTERDAM',
            'packageId': 813,
            'complexType': 'SoftLayer_Container_Product_Order_Virtual_DedicatedHost',
            'prices': [
                {
                    'id': 200269
                }
            ],
            'quantity': 1
        }
        create_dict.return_value = values

        location = 'ams01'
        hostname = 'test'
        domain = 'test.com'
        hourly = True

        self.dedicated_host.verify_order(hostname=hostname,
                                         domain=domain,
                                         location=location,
                                         hourly=hourly)

        create_dict.assert_called_once_with(hostname=hostname,
                                            router=None,
                                            domain=domain,
                                            datacenter=location,
                                            hourly=True)

        self.assert_called_with('SoftLayer_Product_Order',
                                'verifyOrder',
                                args=(values,))

    def test_generate_create_dict_without_router(self):
        self.dedicated_host._get_package = mock.MagicMock()
        self.dedicated_host._get_package.return_value = self._get_package()
        self.dedicated_host._get_backend_router = mock.Mock()
        self.dedicated_host._get_backend_router.return_value = self \
            ._get_routers_sample()

        location = 'ams01'
        hostname = 'test'
        domain = 'test.com'
        hourly = True

        results = self.dedicated_host._generate_create_dict(hostname=hostname,
                                                            domain=domain,
                                                            datacenter=location,
                                                            hourly=hourly)

        testResults = {
            'hardware': [
                {
                    'primaryBackendNetworkComponent': {
                        'router': {
                            'id': 51218
                        }
                    },
                    'domain': u'test.com',
                    'hostname': u'test'
                }
            ],
            'useHourlyPricing': True,
            'location': 'AMSTERDAM',
            'packageId': 813,
            'complexType': 'SoftLayer_Container_Product_Order_Virtual_DedicatedHost',
            'prices': [
                {
                    'id': 200269
                }
            ],
            'quantity': 1
        }

        self.assertEqual(results, testResults)

    def test_generate_create_dict_with_router(self):
        self.dedicated_host._get_package = mock.MagicMock()
        self.dedicated_host._get_package.return_value = self._get_package()

        location = 'ams01'
        router = 55901
        hostname = 'test'
        domain = 'test.com'
        hourly = True

        results = self.dedicated_host._generate_create_dict(
            hostname=hostname,
            router=router,
            domain=domain,
            datacenter=location,
            hourly=hourly)

        testResults = {
            'hardware': [
                {
                    'primaryBackendNetworkComponent': {
                        'router': {
                            'id': 55901
                        }
                    },
                    'domain': u'test.com',
                    'hostname': u'test'
                }
            ],
            'useHourlyPricing': True,
            'location': 'AMSTERDAM',
            'packageId': 813,
            'complexType':
                'SoftLayer_Container_Product_Order_Virtual_DedicatedHost',
            'prices': [
                {
                    'id': 200269
                }
            ],
            'quantity': 1
        }

        self.assertEqual(results, testResults)

    def test_get_package(self):
        mask = '''
        items[
            id,
            description,
            prices,
            itemCategory[categoryCode]
        ],
        regions[location[location[priceGroups]]]
        '''
        self.dedicated_host.ordering_manager = mock.Mock()

        self.dedicated_host.ordering_manager.get_package_by_key.return_value = \
            "test"

        package = self.dedicated_host._get_package()

        package_keyname = 'DEDICATED_HOST'

        self.assertEqual('test', package)
        self.dedicated_host.ordering_manager.get_package_by_key. \
            assert_called_once_with(package_keyname, mask=mask)

    def test_get_package_no_package_found(self):
        mask = '''
        items[
            id,
            description,
            prices,
            itemCategory[categoryCode]
        ],
        regions[location[location[priceGroups]]]
        '''
        self.dedicated_host.ordering_manager = mock.Mock()

        self.dedicated_host.ordering_manager.get_package_by_key.return_value = \
            None

        package_keyname = 'DEDICATED_HOST'

        self.assertRaises(exceptions.SoftLayerError,
                          self.dedicated_host._get_package)

        self.dedicated_host.ordering_manager.get_package_by_key. \
            assert_called_once_with(package_keyname, mask=mask)

    def test_get_location(self):
        regions = [{
            "location": {
                "location": {
                    "name": "dal05",
                }
            }
        }]

        region = {
            'location':
                {
                    'location': {
                        'name': 'dal05',
                    }
                }
        }

        testing = self.dedicated_host._get_location(regions, 'dal05')

        self.assertEqual(testing, region)

    def test_get_location_no_location_found(self):
        regions = [{
            "location": {
                "location": {
                    "name": "dal05",
                }
            }
        }]

        self.assertRaises(exceptions.SoftLayerError,
                          self.dedicated_host._get_location, regions, 'dal10')

    def test_get_create_options(self):
        self.dedicated_host._get_package = mock.MagicMock()
        self.dedicated_host._get_package.return_value = self._get_package()

        results = {
            'dedicated_host': [
                {
                    'key': 10195,
                    'name': '56 Cores X 242 RAM X 1.2 TB'
                }
            ],
            'locations': [
                {
                    'key': 'ams01',
                    'name': 'Amsterdam 1'
                }
            ]
        }

        self.assertEqual(self.dedicated_host.get_create_options(), results)

    def test_get_price(self):
        package = self._get_package()
        item = package['items'][0]
        price_id = 200269

        self.assertEqual(self.dedicated_host._get_price(item), price_id)

    def test_get_price_no_price_found(self):
        package = self._get_package()
        package['items'][0]['prices'][0]['locationGroupId'] = 33
        item = package['items'][0]

        self.assertRaises(exceptions.SoftLayerError,
                          self.dedicated_host._get_price, item)

    def test_get_item(self):
        """Returns the item for ordering a dedicated host."""
        package = self._get_package()

        item = {
            'description': '56 Cores X 242 RAM X 1.2 TB',
            'id': 10195,
            'itemCategory': {
                'categoryCode': 'dedicated_virtual_hosts'
            },
            'prices': [
                {
                    'currentPriceFlag': '',
                    'hourlyRecurringFee': '3.164',
                    'id': 200269,
                    'itemId': 10195,
                    'laborFee': '0',
                    'locationGroupId': '',
                    'onSaleFlag': '',
                    'oneTimeFee': '0',
                    'quantity': '',
                    'recurringFee': '2099',
                    'setupFee': '0',
                    'sort': 0,
                    'tierMinimumThreshold': ''
                }
            ]
        }

        self.assertEqual(self.dedicated_host._get_item(package), item)

    def test_get_item_no_item_found(self):
        package = self._get_package()

        package['items'][0]['description'] = 'not found'

        self.assertRaises(exceptions.SoftLayerError,
                          self.dedicated_host._get_item, package)

    def test_get_backend_router(self):
        location = [
            {
                'isAvailable': 1,
                'locationId': 138124,
                'packageId': 813
            }
        ]

        locId = location[0]['locationId']

        mask = '''
            id,
            hostname
        '''

        host = {
            'cpuCount': 56,
            'memoryCapacity': 242,
            'diskCapacity': 1200,
            'datacenter': {
                'id': locId
            }
        }

        self.dedicated_host.host = mock.Mock()

        routers = self.dedicated_host.host.getAvailableRouters.return_value = \
            self._get_routers_sample()

        routers_test = self.dedicated_host._get_backend_router(location)

        self.assertEqual(routers, routers_test)
        self.dedicated_host.host.getAvailableRouters. \
            assert_called_once_with(host, mask=mask)

    def test_get_backend_router_no_routers_found(self):
        location = []

        self.dedicated_host.host = mock.Mock()

        routers_test = self.dedicated_host._get_backend_router

        self.assertRaises(exceptions.SoftLayerError, routers_test, location)

    def test_get_default_router(self):
        routers = self._get_routers_sample()

        router = 51218

        router_test = self.dedicated_host._get_default_router(routers)

        self.assertEqual(router_test, router)

    def test_get_default_router_no_router_found(self):
        routers = []

        self.assertRaises(exceptions.SoftLayerError,
                          self.dedicated_host._get_default_router, routers)

    def _get_routers_sample(self):
        routers = [
            {
                'hostname': 'bcr01a.dal05',
                'id': 51218
            },
            {
                'hostname': 'bcr02a.dal05',
                'id': 83361
            },
            {
                'hostname': 'bcr03a.dal05',
                'id': 122762
            },
            {
                'hostname': 'bcr04a.dal05',
                'id': 147566
            }
        ]

        return routers

    def _get_package(self):
        package = {
            "items": [
                {
                    "prices": [
                        {
                            "itemId": 10195,
                            "setupFee": "0",
                            "recurringFee": "2099",
                            "tierMinimumThreshold": "",
                            "hourlyRecurringFee": "3.164",
                            "oneTimeFee": "0",
                            "currentPriceFlag": "",
                            "id": 200269,
                            "sort": 0,
                            "onSaleFlag": "",
                            "laborFee": "0",
                            "locationGroupId": "",
                            "quantity": ""
                        }
                    ],
                    "itemCategory": {
                        "categoryCode": "dedicated_virtual_hosts"
                    },
                    "description": "56 Cores X 242 RAM X 1.2 TB",
                    "id": 10195
                }
            ],
            "regions": [
                {
                    "location": {
                        "locationPackageDetails": [
                            {
                                "isAvailable": 1,
                                "locationId": 265592,
                                "packageId": 813
                            }
                        ],
                        "location": {
                            "statusId": 2,
                            "priceGroups": [
                                {
                                    "locationGroupTypeId": 82,
                                    "description": "Location Group 2",
                                    "locationGroupType": {
                                        "name": "PRICING"
                                    },
                                    "securityLevelId": "",
                                    "id": 503,
                                    "name": "Location Group 2"
                                }
                            ],
                            "id": 265592,
                            "name": "ams01",
                            "longName": "Amsterdam 1"
                        }
                    },
                    "keyname": "AMSTERDAM",
                    "description": "AMS01 - Amsterdam",
                    "sortOrder": 0
                }
            ],
            "firstOrderStepId": "",
            "id": 813,
            "isActive": 1,
            "description": "Dedicated Host"
        }

        return package
