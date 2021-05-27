"""
    SoftLayer.tests.managers.hardware_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import copy

from unittest import mock as mock

import SoftLayer
from SoftLayer import fixtures
from SoftLayer import managers
from SoftLayer import testing

MINIMAL_TEST_CREATE_ARGS = {
    'size': 'S1270_8GB_2X1TBSATA_NORAID',
    'hostname': 'unicorn',
    'domain': 'giggles.woo',
    'location': 'wdc01',
    'os': 'UBUNTU_14_64',
    'port_speed': 10,
}


class HardwareTests(testing.TestCase):

    def set_up(self):
        self.hardware = SoftLayer.HardwareManager(self.client)

    def test_init_with_ordering_manager(self):
        ordering_manager = SoftLayer.OrderingManager(self.client)
        mgr = SoftLayer.HardwareManager(self.client, ordering_manager)

        self.assertEqual(mgr.ordering_manager, ordering_manager)

    def test_list_hardware(self):
        # Cast result back to list because list_hardware is now a generator
        results = self.hardware.list_hardware()

        self.assertEqual(results, fixtures.SoftLayer_Account.getHardware)
        self.assert_called_with('SoftLayer_Account', 'getHardware')

    def test_list_hardware_with_filters(self):
        results = self.hardware.list_hardware(
            tags=['tag1', 'tag2'],
            cpus=2,
            memory=1,
            hostname='hostname',
            domain='example.com',
            datacenter='dal05',
            nic_speed=100,
            public_ip='1.2.3.4',
            private_ip='4.3.2.1',
        )

        self.assertEqual(results, fixtures.SoftLayer_Account.getHardware)
        _filter = {
            'hardware': {
                'datacenter': {'name': {'operation': '_= dal05'}},
                'domain': {'operation': '_= example.com'},
                'tagReferences': {
                    'tag': {'name': {
                        'operation': 'in',
                        'options': [
                            {'name': 'data', 'value': ['tag1', 'tag2']}]
                    }}
                },
                'memoryCapacity': {'operation': 1},
                'processorPhysicalCoreAmount': {'operation': 2},
                'hostname': {'operation': '_= hostname'},
                'primaryIpAddress': {'operation': '_= 1.2.3.4'},
                'networkComponents': {'maxSpeed': {'operation': 100}},
                'primaryBackendIpAddress': {'operation': '_= 4.3.2.1'}}
        }
        self.assert_called_with('SoftLayer_Account', 'getHardware',
                                filter=_filter)

    def test_resolve_ids_ip(self):
        _id = self.hardware._get_ids_from_ip('172.16.1.100')
        self.assertEqual(_id, [1000, 1001, 1002, 1003])

        _id = self.hardware._get_ids_from_ip('nope')
        self.assertEqual(_id, [])

        # Now simulate a private IP test
        mock = self.set_mock('SoftLayer_Account', 'getHardware')
        mock.side_effect = [[], [{'id': 99}]]

        _id = self.hardware._get_ids_from_ip('10.0.1.87')

        self.assertEqual(_id, [99])

    def test_resolve_ids_hostname(self):
        _id = self.hardware._get_ids_from_hostname('hardware-test1')
        self.assertEqual(_id, [1000, 1001, 1002, 1003])

    def test_get_hardware(self):
        result = self.hardware.get_hardware(1000)

        self.assertEqual(fixtures.SoftLayer_Hardware_Server.getObject, result)
        self.assert_called_with('SoftLayer_Hardware_Server', 'getObject',
                                identifier=1000)

    def test_reload(self):
        post_uri = 'http://test.sftlyr.ws/test.sh'
        result = self.hardware.reload(1, post_uri=post_uri, ssh_keys=[1701])

        self.assertEqual(result, 'OK')
        self.assert_called_with('SoftLayer_Hardware_Server', 'reloadOperatingSystem',
                                args=('FORCE', {'customProvisionScriptUri': post_uri, 'sshKeyIds': [1701]}),
                                identifier=1)

        result = self.hardware.reload(100, lvm=True)
        self.assertEqual(result, 'OK')
        self.assert_called_with('SoftLayer_Hardware_Server', 'reloadOperatingSystem',
                                args=('FORCE', {'lvmFlag': True}), identifier=100)

    def test_get_create_options(self):
        options = self.hardware.get_create_options()

        extras = {'key': '1_IPV6_ADDRESS', 'name': '1 IPv6 Address'}
        locations = {'key': 'wdc07', 'name': 'Washington 7'}
        operating_systems = {
            'key': 'OS_UBUNTU_14_04_LTS_TRUSTY_TAHR_64_BIT',
            'name': 'Ubuntu / 14.04-64',
            'referenceCode': 'UBUNTU_14_64'
        }

        port_speeds = {
            'key': '10',
            'name': '10 Mbps Public & Private Network Uplinks'
        }
        sizes = {
            'key': 'M1_64X512X25',
            'name': 'M1.64x512x25',
            'hourlyRecurringFee': 0.0,
            'recurringFee': 0.0
        }

        self.assertEqual(options['extras'][0]['key'], extras['key'])
        self.assertEqual(options['locations'][0], locations)
        self.assertEqual(options['operating_systems'][0]['referenceCode'],
                         operating_systems['referenceCode'])
        self.assertEqual(options['port_speeds'][0]['name'], port_speeds['name'])
        self.assertEqual(options['sizes'][0], sizes)

    def test_get_create_options_prices(self):
        options = self.hardware.get_create_options()

        extras = {'key': '1_IPV6_ADDRESS', 'name': '1 IPv6 Address',
                  'prices': [
                      {
                          'hourlyRecurringFee': '0',
                          'id': 272,
                          'locationGroupId': '',
                          'recurringFee': '0',
                      }
                  ]
                  }
        locations = {'key': 'wdc07', 'name': 'Washington 7'}
        operating_systems = {
            'key': 'OS_UBUNTU_14_04_LTS_TRUSTY_TAHR_64_BIT',
            'name': 'Ubuntu / 14.04-64',
            'referenceCode': 'UBUNTU_14_64',
            'prices': [
                {
                    'hourlyRecurringFee': '0',
                    'id': 272,
                    'locationGroupId': '',
                    'recurringFee': '0',
                }
            ]
        }

        port_speeds = {
            'key': '10',
            'name': '10 Mbps Public & Private Network Uplinks',
            'prices': [
                {
                    'hourlyRecurringFee': '0',
                    'id': 272,
                    'locationGroupId': '',
                    'recurringFee': '0',
                }
            ]
        }
        sizes = {
            'key': 'M1_64X512X25',
            'name': 'M1.64x512x25',
            'hourlyRecurringFee': 0.0,
            'recurringFee': 0.0
        }

        self.assertEqual(options['extras'][0]['prices'][0]['hourlyRecurringFee'],
                         extras['prices'][0]['hourlyRecurringFee'])
        self.assertEqual(options['locations'][0], locations)
        self.assertEqual(options['operating_systems'][0]['prices'][0]['locationGroupId'],
                         operating_systems['prices'][0]['locationGroupId'])
        self.assertEqual(options['port_speeds'][0]['prices'][0]['id'], port_speeds['prices'][0]['id'])
        self.assertEqual(options['sizes'][0], sizes)

    def test_get_create_options_prices_by_location(self):
        options = self.hardware.get_create_options('wdc07')

        extras = {'key': '1_IPV6_ADDRESS', 'name': '1 IPv6 Address',
                  'prices': [
                      {
                          'hourlyRecurringFee': '0',
                          'id': 272,
                          'locationGroupId': '',
                          'recurringFee': '0',
                      }
                  ]
                  }
        locations = {'key': 'wdc07', 'name': 'Washington 7'}
        operating_systems = {
            'key': 'OS_UBUNTU_14_04_LTS_TRUSTY_TAHR_64_BIT',
            'name': 'Ubuntu / 14.04-64',
            'referenceCode': 'UBUNTU_14_64',
            'prices': [
                {
                    'hourlyRecurringFee': '0',
                    'id': 272,
                    'locationGroupId': '',
                    'recurringFee': '0',
                }
            ]
        }

        port_speeds = {
            'key': '10',
            'name': '10 Mbps Public & Private Network Uplinks',
            'prices': [
                {
                    'hourlyRecurringFee': '0',
                    'id': 272,
                    'locationGroupId': '',
                    'recurringFee': '0',
                }
            ]
        }
        sizes = {
            'key': 'M1_64X512X25',
            'name': 'M1.64x512x25',
            'hourlyRecurringFee': 0.0,
            'recurringFee': 0.0
        }

        self.assertEqual(options['extras'][0]['prices'][0]['hourlyRecurringFee'],
                         extras['prices'][0]['hourlyRecurringFee'])
        self.assertEqual(options['locations'][0], locations)
        self.assertEqual(options['operating_systems'][0]['prices'][0]['locationGroupId'],
                         operating_systems['prices'][0]['locationGroupId'])
        self.assertEqual(options['port_speeds'][0]['prices'][0]['id'], port_speeds['prices'][0]['id'])
        self.assertEqual(options['sizes'][0], sizes)

    def test_get_hardware_item_prices(self):
        options = self.hardware.get_hardware_item_prices("MONTREAL")
        item_prices = [
            {
                "hourlyRecurringFee": ".093",
                "id": 204015,
                "recurringFee": "62",
                "item": {
                    "description": "4 x 2.0 GHz or higher Cores",
                    "id": 859,
                    "keyName": "GUEST_CORES_4",
                },
                "pricingLocationGroup": {
                    "id": 503,
                    "locations": [
                        {
                            "id": 449610,
                            "longName": "Montreal 1",
                            "name": "mon01",
                            "regions": [
                                {
                                    "description": "MON01 - Montreal",
                                    "keyname": "MONTREAL",
                                }
                            ]
                        }
                    ]
                }
            }
        ]

        self.assertEqual(options[0]['item']['keyName'], item_prices[0]['item']['keyName'])
        self.assertEqual(options[0]['hourlyRecurringFee'], item_prices[0]['hourlyRecurringFee'])

    def test_get_create_options_package_missing(self):
        packages = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        packages.return_value = []

        ex = self.assertRaises(SoftLayer.SoftLayerError, self.hardware.get_create_options)
        self.assertEqual("Package BARE_METAL_SERVER does not exist", str(ex))

    def test_generate_create_dict_no_regions(self):
        packages = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        packages_copy = copy.deepcopy(
            fixtures.SoftLayer_Product_Package.getAllObjects)
        packages_copy[0]['regions'] = []
        packages.return_value = packages_copy

        ex = self.assertRaises(SoftLayer.SoftLayerError,
                               self.hardware._generate_create_dict,
                               **MINIMAL_TEST_CREATE_ARGS)
        self.assertIn("Could not find valid location for: 'wdc01'", str(ex))

    def test_generate_create_dict(self):
        args = {
            'size': 'S1270_8GB_2X1TBSATA_NORAID',
            'hostname': 'unicorn',
            'domain': 'giggles.woo',
            'location': 'wdc07',
            'os': 'OS_UBUNTU_14_04_LTS_TRUSTY_TAHR_64_BIT',
            'port_speed': 10,
            'hourly': True,
            'extras': ['1_IPV6_ADDRESS'],
            'post_uri': 'http://example.com/script.php',
            'ssh_keys': [10],
        }

        package = 'BARE_METAL_SERVER'
        location = 'wdc07'
        item_keynames = [
            '1_IP_ADDRESS',
            'UNLIMITED_SSL_VPN_USERS_1_PPTP_VPN_USER_PER_ACCOUNT',
            'REBOOT_KVM_OVER_IP',
            'OS_UBUNTU_14_04_LTS_TRUSTY_TAHR_64_BIT',
            'BANDWIDTH_0_GB_2',
            '10_MBPS_PUBLIC_PRIVATE_NETWORK_UPLINKS',
            '1_IPV6_ADDRESS'
        ]
        hourly = True
        preset_keyname = 'S1270_8GB_2X1TBSATA_NORAID'
        extras = {
            'hardware': [{
                'domain': 'giggles.woo',
                'hostname': 'unicorn',
            }],
            'provisionScripts': ['http://example.com/script.php'],
            'sshKeys': [{'sshKeyIds': [10]}]
        }

        data = self.hardware._generate_create_dict(**args)

        self.assertEqual(package, data['package_keyname'])
        self.assertEqual(location, data['location'])
        for keyname in item_keynames:
            self.assertIn(keyname, data['item_keynames'])
        self.assertEqual(extras, data['extras'])
        self.assertEqual(preset_keyname, data['preset_keyname'])
        self.assertEqual(hourly, data['hourly'])

    def test_generate_create_dict_by_router_network_component(self):
        args = {
            'size': 'S1270_8GB_2X1TBSATA_NORAID',
            'hostname': 'unicorn',
            'domain': 'giggles.woo',
            'location': 'wdc07',
            'os': 'OS_UBUNTU_14_04_LTS_TRUSTY_TAHR_64_BIT',
            'port_speed': 10,
            'hourly': True,
            'extras': ['1_IPV6_ADDRESS'],
            'public_router': 1111,
            'private_router': 1234
        }

        extras = {
            'hardware': [{
                'domain': 'giggles.woo',
                'hostname': 'unicorn',
                'primaryNetworkComponent': {
                    "router": {
                        "id": 1111
                    }
                },
                'primaryBackendNetworkComponent': {
                    "router": {
                        "id": 1234
                    }
                }
            }]
        }

        data = self.hardware._generate_create_dict(**args)
        self.assertEqual(extras, data['extras'])

    def test_generate_create_dict_network_key(self):
        args = {
            'size': 'S1270_8GB_2X1TBSATA_NORAID',
            'hostname': 'test1',
            'domain': 'test.com',
            'location': 'wdc07',
            'os': 'OS_UBUNTU_14_04_LTS_TRUSTY_TAHR_64_BIT',
            'network': 'NETWORKING',
            'hourly': True,
            'extras': ['1_IPV6_ADDRESS'],
            'post_uri': 'http://example.com/script.php',
            'ssh_keys': [10],
        }

        data = self.hardware._generate_create_dict(**args)
        self.assertIn('NETWORKING', data['item_keynames'])

    @mock.patch('SoftLayer.managers.ordering.OrderingManager.verify_order')
    @mock.patch('SoftLayer.managers.hardware.HardwareManager._generate_create_dict')
    def test_verify_order(self, create_dict, verify_order):
        create_dict.return_value = {'test': 1, 'verify': 1}
        verify_order.return_value = {'test': 2}

        result = self.hardware.verify_order(test=1, verify=1)
        self.assertEqual(2, result['test'])

        create_dict.assert_called_once_with(test=1, verify=1)
        verify_order.assert_called_once_with(test=1, verify=1)

    @mock.patch('SoftLayer.managers.ordering.OrderingManager.place_order')
    @mock.patch('SoftLayer.managers.hardware.HardwareManager._generate_create_dict')
    def test_place_order(self, create_dict, place_order):
        create_dict.return_value = {'test': 1, 'verify': 1}
        place_order.return_value = {'test': 1}
        result = self.hardware.place_order(test=1, verify=1)
        self.assertEqual(1, result['test'])
        create_dict.assert_called_once_with(test=1, verify=1)
        place_order.assert_called_once_with(test=1, verify=1)

    def test_cancel_hardware_without_reason(self):
        mock = self.set_mock('SoftLayer_Hardware_Server', 'getObject')
        mock.return_value = {'id': 987, 'billingItem': {'id': 1234},
                             'openCancellationTicket': {'id': 1234}}

        result = self.hardware.cancel_hardware(987)

        self.assertEqual(result, True)
        reasons = self.hardware.get_cancellation_reasons()
        args = (False, False, reasons['unneeded'], '')
        self.assert_called_with('SoftLayer_Billing_Item', 'cancelItem', identifier=1234, args=args)

    def test_cancel_hardware_with_reason_and_comment(self):
        mock = self.set_mock('SoftLayer_Hardware_Server', 'getObject')
        mock.return_value = {'id': 987, 'billingItem': {'id': 1234},
                             'openCancellationTicket': {'id': 1234}}

        result = self.hardware.cancel_hardware(6327, reason='sales', comment='Test Comment')

        self.assertEqual(result, True)
        reasons = self.hardware.get_cancellation_reasons()
        args = (False, False, reasons['sales'], 'Test Comment')
        self.assert_called_with('SoftLayer_Billing_Item', 'cancelItem', identifier=1234, args=args)

    def test_cancel_hardware(self):
        mock = self.set_mock('SoftLayer_Hardware_Server', 'getObject')
        mock.return_value = {'id': 987, 'billingItem': {'id': 6327},
                             'openCancellationTicket': {'id': 4567}}
        result = self.hardware.cancel_hardware(6327)

        self.assertEqual(result, True)
        self.assert_called_with('SoftLayer_Billing_Item', 'cancelItem',
                                identifier=6327, args=(False, False, 'No longer needed', ''))

    def test_cancel_hardware_no_billing_item(self):
        mock = self.set_mock('SoftLayer_Hardware_Server', 'getObject')
        mock.return_value = {'id': 987, 'openCancellationTicket': {'id': 1234}}

        ex = self.assertRaises(SoftLayer.SoftLayerError,
                               self.hardware.cancel_hardware,
                               6327)
        self.assertEqual("Ticket #1234 already exists for this server", str(ex))

    def test_cancel_hardwareno_billing_item_or_ticket(self):
        mock = self.set_mock('SoftLayer_Hardware_Server', 'getObject')
        mock.return_value = {'id': 987}

        ex = self.assertRaises(SoftLayer.SoftLayerError,
                               self.hardware.cancel_hardware,
                               6327)
        self.assertEqual("Cannot locate billing for the server. The server may already be cancelled.", str(ex))

    def test_cancel_hardware_monthly_now(self):
        mock = self.set_mock('SoftLayer_Hardware_Server', 'getObject')
        mock.return_value = {'id': 987, 'billingItem': {'id': 1234},
                             'openCancellationTicket': {'id': 4567},
                             'hourlyBillingFlag': False}
        with self.assertLogs('SoftLayer.managers.hardware', level='INFO') as logs:
            result = self.hardware.cancel_hardware(987, immediate=True)
        # should be 2 infom essages here
        self.assertEqual(len(logs.records), 2)

        self.assertEqual(result, True)
        self.assert_called_with('SoftLayer_Billing_Item', 'cancelItem',
                                identifier=1234, args=(False, False, 'No longer needed', ''))
        cancel_message = "Please reclaim this server ASAP, it is no longer needed. Thankyou."
        self.assert_called_with('SoftLayer_Ticket', 'addUpdate',
                                identifier=4567, args=({'entry': cancel_message},))

    def test_cancel_hardware_monthly_whenever(self):
        mock = self.set_mock('SoftLayer_Hardware_Server', 'getObject')
        mock.return_value = {'id': 987, 'billingItem': {'id': 6327},
                             'openCancellationTicket': {'id': 4567}}

        with self.assertLogs('SoftLayer.managers.hardware', level='INFO') as logs:
            result = self.hardware.cancel_hardware(987, immediate=False)
        # should be 2 infom essages here
        self.assertEqual(len(logs.records), 1)
        self.assertEqual(result, True)
        self.assert_called_with('SoftLayer_Billing_Item', 'cancelItem',
                                identifier=6327, args=(False, False, 'No longer needed', ''))

    def test_cancel_running_transaction(self):
        mock = self.set_mock('SoftLayer_Hardware_Server', 'getObject')
        mock.return_value = {'id': 987, 'billingItem': {'id': 6327},
                             'activeTransaction': {'id': 4567}}
        self.assertRaises(SoftLayer.SoftLayerError,
                          self.hardware.cancel_hardware,
                          12345)

    def test_change_port_speed_public(self):
        self.hardware.change_port_speed(2, True, 100, 'degraded')

        self.assert_called_with('SoftLayer_Hardware_Server',
                                'setPublicNetworkInterfaceSpeed',
                                identifier=2,
                                args=([100, 'degraded'],))

    def test_change_port_speed_private(self):
        self.hardware.change_port_speed(2, False, 10, 'redundant')

        self.assert_called_with('SoftLayer_Hardware_Server',
                                'setPrivateNetworkInterfaceSpeed',
                                identifier=2,
                                args=([10, 'redundant'],))

    def test_edit_meta(self):
        # Test editing user data
        self.hardware.edit(100, userdata='my data')

        self.assert_called_with('SoftLayer_Hardware_Server',
                                'setUserMetadata',
                                args=(['my data'],),
                                identifier=100)

    def test_edit_blank(self):
        # Now test a blank edit
        self.assertTrue(self.hardware.edit, 100)
        self.assertEqual(self.calls(), [])

    def test_edit(self):
        # Finally, test a full edit
        self.hardware.edit(100,
                           hostname='new-host',
                           domain='new.sftlyr.ws',
                           notes='random notes')

        self.assert_called_with('SoftLayer_Hardware_Server',
                                'editObject',
                                args=({
                                    'hostname': 'new-host',
                                    'domain': 'new.sftlyr.ws',
                                    'notes': 'random notes',
                                },),
                                identifier=100)

    def test_rescue(self):
        result = self.hardware.rescue(1234)

        self.assertEqual(result, True)
        self.assert_called_with('SoftLayer_Hardware_Server',
                                'bootToRescueLayer',
                                identifier=1234)

    def test_update_firmware(self):
        result = self.hardware.update_firmware(100)

        self.assertEqual(result, True)
        self.assert_called_with('SoftLayer_Hardware_Server',
                                'createFirmwareUpdateTransaction',
                                identifier=100, args=(1, 1, 1, 1))

    def test_update_firmware_selective(self):
        result = self.hardware.update_firmware(100,
                                               ipmi=False,
                                               hard_drive=False)

        self.assertEqual(result, True)
        self.assert_called_with('SoftLayer_Hardware_Server',
                                'createFirmwareUpdateTransaction',
                                identifier=100, args=(0, 1, 1, 0))

    def test_reflash_firmware(self):
        result = self.hardware.reflash_firmware(100)

        self.assertEqual(result, True)
        self.assert_called_with('SoftLayer_Hardware_Server',
                                'createFirmwareReflashTransaction',
                                identifier=100, args=(1, 1, 1))

    def test_reflash_firmware_selective(self):
        result = self.hardware.reflash_firmware(100,
                                                raid_controller=False,
                                                bios=False)

        self.assertEqual(result, True)
        self.assert_called_with('SoftLayer_Hardware_Server',
                                'createFirmwareReflashTransaction',
                                identifier=100, args=(1, 0, 0))

    def test_get_tracking_id(self):
        result = self.hardware.get_tracking_id(1234)
        self.assert_called_with('SoftLayer_Hardware_Server', 'getMetricTrackingObjectId')
        self.assertEqual(result, 1000)

    def test_get_bandwidth_data(self):
        result = self.hardware.get_bandwidth_data(1234, '2019-01-01', '2019-02-01', 'public', 1000)
        self.assert_called_with('SoftLayer_Metric_Tracking_Object',
                                'getBandwidthData',
                                args=('2019-01-01', '2019-02-01', 'public', 1000),
                                identifier=1000)
        self.assertEqual(result[0]['type'], 'cpu0')

    def test_get_bandwidth_allocation(self):
        result = self.hardware.get_bandwidth_allocation(1234)
        self.assert_called_with('SoftLayer_Hardware_Server', 'getBandwidthAllotmentDetail', identifier=1234)
        self.assert_called_with('SoftLayer_Hardware_Server', 'getBillingCycleBandwidthUsage', identifier=1234)
        self.assertEqual(result['allotment']['amount'], '250')
        self.assertEqual(result['usage'][0]['amountIn'], '.448')

    def test_get_bandwidth_allocation_with_allotment(self):
        mock = self.set_mock('SoftLayer_Hardware_Server', 'getBandwidthAllotmentDetail')
        mock.return_value = {
            "allocationId": 11111,
            "id": 22222,
            "allocation": {
                "amount": "2000"
            }
        }

        result = self.hardware.get_bandwidth_allocation(1234)

        self.assertEqual(2000, int(result['allotment']['amount']))

    def test_get_bandwidth_allocation_no_allotment(self):
        mock = self.set_mock('SoftLayer_Hardware_Server', 'getBandwidthAllotmentDetail')
        mock.return_value = None

        result = self.hardware.get_bandwidth_allocation(1234)

        self.assertEqual(None, result['allotment'])

    def test_get_storage_iscsi_details(self):
        mock = self.set_mock('SoftLayer_Hardware_Server', 'getAttachedNetworkStorages')
        mock.return_value = [
            {
                "accountId": 11111,
                "capacityGb": 12000,
                "id": 3777123,
                "nasType": "ISCSI",
                "username": "SL02SEL31111-9",
            }
        ]

        result = self.hardware.get_storage_details(1234, 'ISCSI')

        self.assertEqual([{
            "accountId": 11111,
            "capacityGb": 12000,
            "id": 3777123,
            "nasType": "ISCSI",
            "username": "SL02SEL31111-9",
        }], result)

    def test_get_storage_iscsi_empty_details(self):
        mock = self.set_mock('SoftLayer_Hardware_Server', 'getAttachedNetworkStorages')
        mock.return_value = []

        result = self.hardware.get_storage_details(1234, 'ISCSI')

        self.assertEqual([], result)

    def test_get_storage_nas_details(self):
        mock = self.set_mock('SoftLayer_Hardware_Server', 'getAttachedNetworkStorages')
        mock.return_value = [
            {
                "accountId": 11111,
                "capacityGb": 12000,
                "id": 3777111,
                "nasType": "NAS",
                "username": "SL02SEL32222-9",
            }
        ]

        result = self.hardware.get_storage_details(1234, 'NAS')

        self.assertEqual([{
            "accountId": 11111,
            "capacityGb": 12000,
            "id": 3777111,
            "nasType": "NAS",
            "username": "SL02SEL32222-9",
        }], result)

    def test_get_storage_nas_empty_details(self):
        mock = self.set_mock('SoftLayer_Hardware_Server', 'getAttachedNetworkStorages')
        mock.return_value = []

        result = self.hardware.get_storage_details(1234, 'NAS')

        self.assertEqual([], result)

    def test_get_storage_credentials(self):
        mock = self.set_mock('SoftLayer_Hardware_Server', 'getAllowedHost')
        mock.return_value = {
            "accountId": 11111,
            "id": 33333,
            "name": "iqn.2020-03.com.ibm:sl02su11111-v62941551",
            "resourceTableName": "HARDWARE",
            "credential": {
                "accountId": "11111",
                "id": 44444,
                "password": "SjFDCpHrjskfj",
                "username": "SL02SU11111-V62941551"
            }
        }

        result = self.hardware.get_storage_credentials(1234)

        self.assertEqual({
            "accountId": 11111,
            "id": 33333,
            "name": "iqn.2020-03.com.ibm:sl02su11111-v62941551",
            "resourceTableName": "HARDWARE",
            "credential": {
                "accountId": "11111",
                "id": 44444,
                "password": "SjFDCpHrjskfj",
                "username": "SL02SU11111-V62941551"
            }
        }, result)

    def test_get_none_storage_credentials(self):
        mock = self.set_mock('SoftLayer_Hardware_Server', 'getAllowedHost')
        mock.return_value = None

        result = self.hardware.get_storage_credentials(1234)

        self.assertEqual(None, result)

    def test_get_hard_drives(self):
        mock = self.set_mock('SoftLayer_Hardware_Server', 'getHardDrives')
        mock.return_value = [
            {
                "id": 11111,
                "serialNumber": "z1w4sdf",
                "serviceProviderId": 1,
                "hardwareComponentModel": {
                    "capacity": "1000",
                    "description": "SATAIII:2000:8300:Constellation",
                    "id": 111,
                    "manufacturer": "Seagate",
                    "name": "Constellation ES",
                    "hardwareGenericComponentModel": {
                        "capacity": "1000",
                        "units": "GB",
                        "hardwareComponentType": {
                            "id": 1,
                            "keyName": "HARD_DRIVE",
                            "type": "Hard Drive",
                            "typeParentId": 5
                        }
                    }
                }
            }
        ]

        result = self.hardware.get_hard_drives(1234)

        self.assertEqual([
            {
                "id": 11111,
                "serialNumber": "z1w4sdf",
                "serviceProviderId": 1,
                "hardwareComponentModel": {
                    "capacity": "1000",
                    "description": "SATAIII:2000:8300:Constellation",
                    "id": 111,
                    "manufacturer": "Seagate",
                    "name": "Constellation ES",
                    "hardwareGenericComponentModel": {
                        "capacity": "1000",
                        "units": "GB",
                        "hardwareComponentType": {
                            "id": 1,
                            "keyName": "HARD_DRIVE",
                            "type": "Hard Drive",
                            "typeParentId": 5
                        }
                    }
                }
            }
        ], result)

    def test_get_hard_drive_empty(self):
        mock = self.set_mock('SoftLayer_Hardware_Server', 'getHardDrives')
        mock.return_value = []

        result = self.hardware.get_hard_drives(1234)

        self.assertEqual([], result)

    def test_get_hardware_guests_empty_virtualHost(self):
        mock = self.set_mock('SoftLayer_Hardware_Server', 'getVirtualHost')
        mock.return_value = None

        result = self.hardware.get_hardware_guests(1234)

        self.assertEqual(None, result)

    def test_get_hardware_guests(self):
        mock = self.set_mock('SoftLayer_Virtual_Host', 'getGuests')
        mock.return_value = [
            {
                "accountId": 11111,
                "hostname": "NSX-T Manager",
                "id": 22222,
                "maxCpu": 16,
                "maxCpuUnits": "CORE",
                "maxMemory": 49152,
                "powerState": {
                    "keyName": "RUNNING",
                    "name": "Running"
                },
                "status": {
                    "keyName": "ACTIVE",
                    "name": "Active"
                }
            }]

        result = self.hardware.get_hardware_guests(1234)

        self.assertEqual("NSX-T Manager", result[0]['hostname'])

    def test_authorize_storage(self):
        options = self.hardware.authorize_storage(1234, "SL01SEL301234-11")

        self.assertEqual(True, options)

    def test_authorize_storage_empty(self):
        mock = self.set_mock('SoftLayer_Account', 'getNetworkStorage')
        mock.return_value = []
        self.assertRaises(SoftLayer.exceptions.SoftLayerError,
                          self.hardware.authorize_storage,
                          1234, "#")

    def test_get_price_id_memory_capacity(self):
        upgrade_prices = [
            {'categories': [{'categoryCode': 'ram'}], 'item': {'capacity': 1}, 'id': 99}
        ]
        result = self.hardware._get_prices_for_upgrade_option(upgrade_prices, 'memory', 1)
        self.assertEqual(99, result)

    def test_get_price_id_mismatch_capacity(self):
        upgrade_prices = [
            {'categories': [{'categoryCode': 'ram1'}], 'item': {'capacity': 1}, 'id': 90},
            {'categories': [{'categoryCode': 'ram'}], 'item': {'capacity': 2}, 'id': 91},
            {'categories': [{'categoryCode': 'ram'}], 'item': {'capacity': 1}, 'id': 92},
        ]
        result = self.hardware._get_prices_for_upgrade_option(upgrade_prices, 'memory', 1)
        self.assertEqual(92, result)

    def test_get_price_id_disk_capacity(self):
        upgrade_prices = [
            {'categories': [{'categoryCode': 'disk1'}], 'item': {'capacity': 1}, 'id': 99}
        ]
        result = self.hardware._get_prices_for_upgrade_option(upgrade_prices, 'disk1', 1)
        self.assertEqual(99, result['id'])

    def test_upgrade(self):
        result = self.hardware.upgrade(1, memory=32)

        self.assertEqual(result['orderId'], 1234)
        self.assert_called_with('SoftLayer_Product_Order', 'placeOrder')
        call = self.calls('SoftLayer_Product_Order', 'placeOrder')[0]
        order_container = call.args[0]
        self.assertEqual(order_container['prices'], [{'id': 209391}])

    def test_upgrade_add_disk(self):
        disk_list = list()
        disks = {'description': 'add_disk', 'capacity': 1000, 'number': 2}
        disk_list.append(disks)
        result = self.hardware.upgrade(1, disk=disk_list)

        self.assertEqual(result['orderId'], 1234)
        self.assert_called_with('SoftLayer_Product_Order', 'placeOrder')
        call = self.calls('SoftLayer_Product_Order', 'placeOrder')[0]
        order_container = call.args[0]
        self.assertEqual(order_container['prices'][0]['id'], 49759)

    def test_upgrade_resize_disk(self):
        disk_list = list()
        disks = {'description': 'resize_disk', 'capacity': 1000, 'number': 1}
        disk_list.append(disks)
        result = self.hardware.upgrade(1, disk=disk_list)

        self.assertEqual(result['orderId'], 1234)
        self.assert_called_with('SoftLayer_Product_Order', 'placeOrder')
        call = self.calls('SoftLayer_Product_Order', 'placeOrder')[0]
        order_container = call.args[0]
        self.assertEqual(order_container['prices'][0]['id'], 49759)

    def test_upgrade_blank(self):
        result = self.hardware.upgrade(1)

        self.assertEqual(result, None)
        self.assertEqual(self.calls('SoftLayer_Product_Order', 'placeOrder'), [])

    def test_upgrade_full(self):
        result = self.hardware.upgrade(1, memory=32, nic_speed="10000 Redundant", drive_controller="RAID",
                                       public_bandwidth=500, test=False)

        self.assertEqual(result['orderId'], 1234)
        self.assert_called_with('SoftLayer_Product_Order', 'placeOrder')
        call = self.calls('SoftLayer_Product_Order', 'placeOrder')[0]
        order_container = call.args[0]
        self.assertIn({'id': 209391}, order_container['prices'])
        self.assertIn({'id': 21525}, order_container['prices'])
        self.assertIn({'id': 22482}, order_container['prices'])
        self.assertIn({'id': 50357}, order_container['prices'])

    def test_get_components(self):
        result = self.hardware.get_components(1234)
        components = [{'hardwareComponentModelId': 147,
                       'hardwareId': 1234,
                       'id': 369,
                       'modifyDate': '2017-11-10T16:59:38-06:00',
                       'serviceProviderId': 1,
                       'hardwareComponentModel':
                           {'name': 'IMM2 - Onboard',
                            'firmwares':
                                [{'createDate': '2020-09-24T13:46:29-06:00',
                                  'version': '5.60'},
                                 {'createDate': '2019-10-14T16:51:12-06:00',
                                  'version': '5.10'}]}}]
        self.assert_called_with('SoftLayer_Hardware_Server', 'getComponents')
        self.assertEqual(result, components)
        self.assertEqual(result[0]['hardwareId'], 1234)
        self.assertEqual(result[0]['hardwareComponentModel']['name'], 'IMM2 - Onboard')
        self.assertEqual(result[0]['hardwareComponentModel']['firmwares'][0]['version'], '5.60')


class HardwareHelperTests(testing.TestCase):

    def set_up(self):
        self.items = [
            {
                "itemCategory": {"categoryCode": "port_speed"},
                "capacity": 100,
                "attributes": [
                    {'attributeTypeKeyName': 'NON_LACP'},
                    {'attributeTypeKeyName': 'IS_PRIVATE_NETWORK_ONLY'}
                ],
                "keyName": "ITEM_1",
                "prices": [{"id": 1, "locationGroupId": 100}]
            },
            {
                "itemCategory": {"categoryCode": "port_speed"},
                "capacity": 200,
                "attributes": [
                    {'attributeTypeKeyName': 'YES_LACP'},
                    {'attributeTypeKeyName': 'IS_PRIVATE_NETWORK_ONLY'}
                ],
                "keyName": "ITEM_2",
                "prices": [{"id": 1, "locationGroupId": 151}]
            },
            {
                "itemCategory": {"categoryCode": "port_speed"},
                "capacity": 200,
                "attributes": [
                    {'attributeTypeKeyName': 'YES_LACP'},
                    {'attributeTypeKeyName': 'IS_PRIVATE_NETWORK_ONLY'}
                ],
                "keyName": "ITEM_3",
                "prices": [{"id": 1, "locationGroupId": 51}]
            },
            {
                "itemCategory": {"categoryCode": "bandwidth"},
                "capacity": 0.0,
                "attributes": [],
                "keyName": "HOURLY_BANDWIDTH_1",
                "prices": [{"id": 1, "locationGroupId": 51, "hourlyRecurringFee": 1.0, "recurringFee": 1.0}]
            },
            {
                "itemCategory": {"categoryCode": "bandwidth"},
                "capacity": 10.0,
                "attributes": [],
                "keyName": "MONTHLY_BANDWIDTH_1",
                "prices": [{"id": 1, "locationGroupId": 151, "recurringFee": 1.0}]
            },
            {
                "itemCategory": {"categoryCode": "bandwidth"},
                "capacity": 10.0,
                "attributes": [],
                "keyName": "MONTHLY_BANDWIDTH_2",
                "prices": [{"id": 1, "locationGroupId": 51, "recurringFee": 1.0}]
            },
        ]
        self.location = {'location': {'location': {'priceGroups': [{'id': 50}, {'id': 51}]}}}

    def test_bandwidth_key(self):
        result = managers.hardware._get_bandwidth_key(self.items, True, False, self.location)
        self.assertEqual('HOURLY_BANDWIDTH_1', result)
        result = managers.hardware._get_bandwidth_key(self.items, False, True, self.location)
        self.assertEqual('HOURLY_BANDWIDTH_1', result)
        result = managers.hardware._get_bandwidth_key(self.items, False, False, self.location)
        self.assertEqual('MONTHLY_BANDWIDTH_2', result)
        ex = self.assertRaises(SoftLayer.SoftLayerError,
                               managers.hardware._get_bandwidth_key, [], True, False, self.location)
        self.assertEqual("Could not find valid price for bandwidth option", str(ex))

    def test_port_speed_key(self):
        result = managers.hardware._get_port_speed_key(self.items, 200, True, self.location)
        self.assertEqual("ITEM_3", result)

    def test_port_speed_key_exception(self):
        items = []
        location = {}
        ex = self.assertRaises(SoftLayer.SoftLayerError,
                               managers.hardware._get_port_speed_key, items, 999, False, location)
        self.assertEqual("Could not find valid price for port speed: '999'", str(ex))

    def test_matches_location(self):
        price = {'id': 1, 'locationGroupId': 51, 'recurringFee': 99}

        self.assertTrue(managers.hardware._matches_location(price, self.location))
        price['locationGroupId'] = 99999
        self.assertFalse(managers.hardware._matches_location(price, self.location))

    def test_is_bonded(self):
        item_non_lacp = {'attributes': [{'attributeTypeKeyName': 'NON_LACP'}]}
        item_lacp = {'attributes': [{'attributeTypeKeyName': 'YES_LACP'}]}
        self.assertFalse(managers.hardware._is_bonded(item_non_lacp))
        self.assertTrue(managers.hardware._is_bonded(item_lacp))

    def test_is_private(self):
        item_private = {'attributes': [{'attributeTypeKeyName': 'IS_PRIVATE_NETWORK_ONLY'}]}
        item_public = {'attributes': [{'attributeTypeKeyName': 'NOT_PRIVATE_NETWORK_ONLY'}]}
        self.assertTrue(managers.hardware._is_private_port_speed_item(item_private))
        self.assertFalse(managers.hardware._is_private_port_speed_item(item_public))
