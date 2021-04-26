"""
    SoftLayer.tests.managers.dedicated_host_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
from unittest import mock as mock

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

        mask = ('''
                id,
                name,
                cpuCount,
                memoryCapacity,
                diskCapacity,
                createDate,
                modifyDate,
                backendRouter[
                    id,
                    hostname,
                    domain
                ],
                billingItem[
                    id,
                    nextInvoiceTotalRecurringAmount,
                    children[
                        categoryCode,
                        nextInvoiceTotalRecurringAmount
                    ],
                    orderItem[
                        id,
                        order.userRecord[
                            username
                        ]
                    ]
                ],
                datacenter[
                    id,
                    name,
                    longName
                ],
                guests[
                    id,
                    hostname,
                    domain,
                    uuid
                ],
                guestCount
            ''')
        self.dedicated_host.host.getObject.assert_called_once_with(id=12345, mask=mask)

    def test_place_order(self):
        create_dict = self.dedicated_host._generate_create_dict = mock.Mock()

        values = {
            'hardware': [
                {
                    'primaryBackendNetworkComponent': {
                        'router': {
                            'id': 12345
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
                    'id': 12345
                }
            ],
            'quantity': 1
        }
        create_dict.return_value = values

        location = 'dal05'
        hostname = 'test'
        domain = 'test.com'
        hourly = True
        flavor = '56_CORES_X_242_RAM_X_1_4_TB'

        self.dedicated_host.place_order(hostname=hostname,
                                        domain=domain,
                                        location=location,
                                        flavor=flavor,
                                        hourly=hourly)

        create_dict.assert_called_once_with(hostname=hostname,
                                            router=None,
                                            domain=domain,
                                            datacenter=location,
                                            flavor=flavor,
                                            hourly=True)

        self.assert_called_with('SoftLayer_Product_Order',
                                'placeOrder',
                                args=(values,))

    def test_place_order_with_gpu(self):
        create_dict = self.dedicated_host._generate_create_dict = mock.Mock()

        values = {
            'hardware': [
                {
                    'primaryBackendNetworkComponent': {
                        'router': {
                            'id': 12345
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
                    'id': 12345
                }
            ],
            'quantity': 1
        }
        create_dict.return_value = values

        location = 'dal05'
        hostname = 'test'
        domain = 'test.com'
        hourly = True
        flavor = '56_CORES_X_484_RAM_X_1_5_TB_X_2_GPU_P100'

        self.dedicated_host.place_order(hostname=hostname,
                                        domain=domain,
                                        location=location,
                                        flavor=flavor,
                                        hourly=hourly)

        create_dict.assert_called_once_with(hostname=hostname,
                                            router=None,
                                            domain=domain,
                                            datacenter=location,
                                            flavor=flavor,
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
                            'id': 12345
                        }
                    },
                    'domain': 'test.com',
                    'hostname': 'test'
                }
            ],
            'useHourlyPricing': True,
            'location': 'AMSTERDAM',
            'packageId': 813,
            'complexType': 'SoftLayer_Container_Product_Order_Virtual_DedicatedHost',
            'prices': [
                {
                    'id': 12345
                }
            ],
            'quantity': 1
        }
        create_dict.return_value = values

        location = 'dal05'
        hostname = 'test'
        domain = 'test.com'
        hourly = True
        flavor = '56_CORES_X_242_RAM_X_1_4_TB'

        self.dedicated_host.verify_order(hostname=hostname,
                                         domain=domain,
                                         location=location,
                                         flavor=flavor,
                                         hourly=hourly)

        create_dict.assert_called_once_with(hostname=hostname,
                                            router=None,
                                            domain=domain,
                                            datacenter=location,
                                            flavor=flavor,
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

        location = 'dal05'
        hostname = 'test'
        domain = 'test.com'
        hourly = True
        flavor = '56_CORES_X_242_RAM_X_1_4_TB'

        results = self.dedicated_host._generate_create_dict(hostname=hostname,
                                                            domain=domain,
                                                            datacenter=location,
                                                            flavor=flavor,
                                                            hourly=hourly)

        testResults = {
            'hardware': [
                {
                    'primaryBackendNetworkComponent': {
                        'router': {
                            'id': 12345
                        }
                    },
                    'domain': 'test.com',
                    'hostname': 'test'
                }
            ],
            'useHourlyPricing': True,
            'location': 'DALLAS05',
            'packageId': 813,
            'complexType': 'SoftLayer_Container_Product_Order_Virtual_DedicatedHost',
            'prices': [
                {
                    'id': 12345
                }
            ],
            'quantity': 1
        }

        self.assertEqual(results, testResults)

    def test_generate_create_dict_with_router(self):
        self.dedicated_host._get_package = mock.MagicMock()
        self.dedicated_host._get_package.return_value = self._get_package()
        self.dedicated_host._get_default_router = mock.Mock()
        self.dedicated_host._get_default_router.return_value = 12345

        location = 'dal05'
        router = 12345
        hostname = 'test'
        domain = 'test.com'
        hourly = True
        flavor = '56_CORES_X_242_RAM_X_1_4_TB'

        results = self.dedicated_host._generate_create_dict(
            hostname=hostname,
            router=router,
            domain=domain,
            datacenter=location,
            flavor=flavor,
            hourly=hourly)

        testResults = {
            'hardware': [
                {
                    'primaryBackendNetworkComponent': {
                        'router': {
                            'id': 12345
                        }
                    },
                    'domain': 'test.com',
                    'hostname': 'test'
                }
            ],
            'useHourlyPricing': True,
            'location': 'DALLAS05',
            'packageId': 813,
            'complexType':
                'SoftLayer_Container_Product_Order_Virtual_DedicatedHost',
            'prices': [
                {
                    'id': 12345
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
            capacity,
            keyName,
            itemCategory[categoryCode],
            bundleItems[capacity,keyName,categories[categoryCode],hardwareGenericComponentModel[id,
            hardwareComponentType[keyName]]]
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
        packages = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        packages.return_value = []

        self.assertRaises(exceptions.SoftLayerError, self.dedicated_host._get_package)

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
            'dedicated_host': [{
                'key': '56_CORES_X_242_RAM_X_1_4_TB',
                'name': '56 Cores X 242 RAM X 1.2 TB'
            }],
            'locations': [
                {
                    'key': 'ams01',
                    'name': 'Amsterdam 1'
                },
                {
                    'key': 'dal05',
                    'name': 'Dallas 5'
                }
            ]
        }

        self.assertEqual(self.dedicated_host.get_create_options(), results)

    def test_get_price(self):
        package = self._get_package()
        item = package['items'][0]
        price_id = 12345

        self.assertEqual(self.dedicated_host._get_price(item), price_id)

    def test_get_price_no_price_found(self):
        package = self._get_package()
        package['items'][0]['prices'][0]['locationGroupId'] = 33
        item = package['items'][0]

        self.assertRaises(exceptions.SoftLayerError, self.dedicated_host._get_price, item)

    def test_get_item(self):
        """Returns the item for ordering a dedicated host."""
        package = self._get_package()
        flavor = '56_CORES_X_242_RAM_X_1_4_TB'

        item = {
            'bundleItems': [{
                'capacity': '1200',
                'keyName': '1_4_TB_LOCAL_STORAGE_DEDICATED_HOST_CAPACITY',
                'categories': [{
                    'categoryCode': 'dedicated_host_disk'
                }]
            },
                {
                    'capacity': '242',
                    'keyName': '242_GB_RAM',
                    'categories': [{
                        'categoryCode': 'dedicated_host_ram'
                    }]
            }],
            'capacity': '56',
            'description': '56 Cores X 242 RAM X 1.2 TB',
            'id': 12345,
            'itemCategory': {
                'categoryCode': 'dedicated_virtual_hosts'
            },
            'keyName': '56_CORES_X_242_RAM_X_1_4_TB',
            'prices': [{
                'hourlyRecurringFee': '3.164',
                'id': 12345,
                'itemId': 12345,
                'recurringFee': '2099',
            }]
        }

        self.assertEqual(self.dedicated_host._get_item(package, flavor), item)

    def test_get_item_no_item_found(self):
        package = self._get_package()

        flavor = '56_CORES_X_242_RAM_X_1_4_TB'
        package['items'][0]['keyName'] = 'not found'

        self.assertRaises(exceptions.SoftLayerError, self.dedicated_host._get_item, package, flavor)

    def test_get_backend_router(self):
        location = [
            {
                'isAvailable': 1,
                'locationId': 12345,
                'packageId': 813
            }
        ]

        locId = location[0]['locationId']

        mask = '''
            id,
            hostname
        '''

        host = {
            'cpuCount': '56',
            'memoryCapacity': '242',
            'diskCapacity': '1200',
            'datacenter': {
                'id': locId
            }
        }

        self.dedicated_host.host = mock.Mock()

        routers = self.dedicated_host.host.getAvailableRouters.return_value = \
            self._get_routers_sample()

        item = self._get_package()['items'][0]

        routers_test = self.dedicated_host._get_backend_router(location, item)

        self.assertEqual(routers, routers_test)
        self.dedicated_host.host.getAvailableRouters.assert_called_once_with(host, mask=mask)

    def test_get_backend_router_no_routers_found(self):
        location = []

        self.dedicated_host.host = mock.Mock()

        routers_test = self.dedicated_host._get_backend_router

        item = self._get_package()['items'][0]

        self.assertRaises(exceptions.SoftLayerError, routers_test, location, item)

    def test_get_default_router(self):
        routers = self._get_routers_sample()

        router = 12345

        router_test = self.dedicated_host._get_default_router(routers, 'bcr01a.dal05')

        self.assertEqual(router_test, router)

    def test_get_default_router_no_router_found(self):
        routers = []

        self.assertRaises(exceptions.SoftLayerError,
                          self.dedicated_host._get_default_router, routers, 'notFound')

    def test_cancel_host(self):
        result = self.dedicated_host.cancel_host(789)

        self.assertEqual(result, True)
        self.assert_called_with('SoftLayer_Virtual_DedicatedHost', 'deleteObject', identifier=789)

    def test_cancel_guests(self):
        vs1 = {'id': 987, 'fullyQualifiedDomainName': 'foobar.example.com'}
        vs2 = {'id': 654, 'fullyQualifiedDomainName': 'wombat.example.com'}
        self.dedicated_host.host = mock.Mock()
        self.dedicated_host.host.getGuests.return_value = [vs1, vs2]

        # Expected result
        vs_status1 = {'id': 987, 'fqdn': 'foobar.example.com', 'status': 'Cancelled'}
        vs_status2 = {'id': 654, 'fqdn': 'wombat.example.com', 'status': 'Cancelled'}
        delete_status = [vs_status1, vs_status2]

        result = self.dedicated_host.cancel_guests(789)

        self.assertEqual(result, delete_status)

    def test_cancel_guests_empty_list(self):
        self.dedicated_host.host = mock.Mock()
        self.dedicated_host.host.getGuests.return_value = []

        result = self.dedicated_host.cancel_guests(789)

        self.assertEqual(result, [])

    def test_delete_guest(self):
        result = self.dedicated_host._delete_guest(123)
        self.assertEqual(result, 'Cancelled')

        # delete_guest should return the exception message in case it fails
        error_raised = SoftLayer.SoftLayerAPIError('SL Exception', 'SL message')
        self.dedicated_host.guest = mock.Mock()
        self.dedicated_host.guest.deleteObject.side_effect = error_raised

        result = self.dedicated_host._delete_guest(369)
        self.assertEqual(result, 'Exception: SL message')

    def _get_routers_sample(self):
        routers = [
            {
                'hostname': 'bcr01a.dal05',
                'id': 12345
            },
            {
                'hostname': 'bcr02a.dal05',
                'id': 12346
            },
            {
                'hostname': 'bcr03a.dal05',
                'id': 12347
            },
            {
                'hostname': 'bcr04a.dal05',
                'id': 12348
            }
        ]

        return routers

    def _get_package(self):
        package = {
            "items": [
                {
                    "capacity": "56",
                    "description": "56 Cores X 242 RAM X 1.2 TB",
                    "bundleItems": [
                        {
                            "capacity": "1200",
                            "keyName": "1_4_TB_LOCAL_STORAGE_DEDICATED_HOST_CAPACITY",
                            "categories": [
                                {
                                    "categoryCode": "dedicated_host_disk"
                                }
                            ]
                        },
                        {
                            "capacity": "242",
                            "keyName": "242_GB_RAM",
                            "categories": [
                                {
                                    "categoryCode": "dedicated_host_ram"
                                }
                            ]
                        }
                    ],
                    "prices": [
                        {
                            "itemId": 12345,
                            "recurringFee": "2099",
                            "hourlyRecurringFee": "3.164",
                            "id": 12345,
                        }
                    ],
                    "keyName": "56_CORES_X_242_RAM_X_1_4_TB",
                    "id": 12345,
                    "itemCategory": {
                        "categoryCode": "dedicated_virtual_hosts"
                    },
                }
            ],
            "regions": [
                {
                    "location": {
                        "locationPackageDetails": [
                            {
                                "locationId": 12345,
                                "packageId": 813
                            }
                        ],
                        "location": {
                            "id": 12345,
                            "name": "ams01",
                            "longName": "Amsterdam 1"
                        }
                    },
                    "keyname": "AMSTERDAM",
                    "description": "AMS01 - Amsterdam",
                    "sortOrder": 0
                },
                {
                    "location": {
                        "locationPackageDetails": [
                            {
                                "isAvailable": 1,
                                "locationId": 12345,
                                "packageId": 813
                            }
                        ],
                        "location": {
                            "id": 12345,
                            "name": "dal05",
                            "longName": "Dallas 5"
                        }
                    },
                    "keyname": "DALLAS05",
                    "description": "DAL05 - Dallas",
                }

            ],
            "id": 813,
            "description": "Dedicated Host"
        }

        return package

    def test_list_guests(self):
        results = self.dedicated_host.list_guests(12345)

        for result in results:
            self.assertIn(result['id'], [200, 202])
        self.assert_called_with('SoftLayer_Virtual_DedicatedHost', 'getGuests', identifier=12345)

    def test_list_guests_with_filters(self):
        self.dedicated_host.list_guests(12345, tags=['tag1', 'tag2'], cpus=2, memory=1024,
                                        hostname='hostname', domain='example.com', nic_speed=100,
                                        public_ip='1.2.3.4', private_ip='4.3.2.1')

        _filter = {
            'guests': {
                'domain': {'operation': '_= example.com'},
                'tagReferences': {
                    'tag': {'name': {
                        'operation': 'in',
                        'options': [{
                            'name': 'data', 'value': ['tag1', 'tag2']}]}}},
                'maxCpu': {'operation': 2},
                'maxMemory': {'operation': 1024},
                'hostname': {'operation': '_= hostname'},
                'networkComponents': {'maxSpeed': {'operation': 100}},
                'primaryIpAddress': {'operation': '_= 1.2.3.4'},
                'primaryBackendIpAddress': {'operation': '_= 4.3.2.1'}
            }
        }
        self.assert_called_with('SoftLayer_Virtual_DedicatedHost', 'getGuests',
                                identifier=12345, filter=_filter)
