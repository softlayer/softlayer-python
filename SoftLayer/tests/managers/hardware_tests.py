"""
    SoftLayer.tests.managers.hardware_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import copy

import mock

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
        self.assert_called_with('SoftLayer_Hardware_Server',
                                'reloadOperatingSystem',
                                args=('FORCE',
                                      {'customProvisionScriptUri': post_uri,
                                       'sshKeyIds': [1701]}),
                                identifier=1)

    def test_get_create_options(self):
        options = self.hardware.get_create_options()

        expected = {
            'extras': [{'key': '1_IPV6_ADDRESS', 'name': '1 IPv6 Address'}],
            'locations': [{'key': 'wdc01', 'name': 'Washington 1'}],
            'operating_systems': [{'key': 'UBUNTU_14_64',
                                   'name': 'Ubuntu / 14.04-64'}],
            'port_speeds': [{
                'key': '10',
                'name': '10 Mbps Public & Private Network Uplinks'
            }],
            'sizes': [{
                'key': 'S1270_8GB_2X1TBSATA_NORAID',
                'name': 'Single Xeon 1270, 8GB Ram, 2x1TB SATA disks, Non-RAID'
            }]
        }

        self.assertEqual(options, expected)

    def test_get_create_options_package_missing(self):
        packages = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        packages.return_value = []

        ex = self.assertRaises(SoftLayer.SoftLayerError,
                               self.hardware.get_create_options)
        self.assertEqual("Ordering package not found", str(ex))

    def test_generate_create_dict_no_items(self):
        packages = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        packages_copy = copy.deepcopy(
            fixtures.SoftLayer_Product_Package.getAllObjects)
        packages_copy[0]['items'] = []
        packages.return_value = packages_copy

        ex = self.assertRaises(SoftLayer.SoftLayerError,
                               self.hardware._generate_create_dict,
                               location="wdc01")
        self.assertIn("Could not find valid price", str(ex))

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

    def test_generate_create_dict_invalid_size(self):
        args = {
            'size': 'UNKNOWN_SIZE',
            'hostname': 'unicorn',
            'domain': 'giggles.woo',
            'location': 'wdc01',
            'os': 'UBUNTU_14_64',
            'port_speed': 10,
        }

        ex = self.assertRaises(SoftLayer.SoftLayerError,
                               self.hardware._generate_create_dict, **args)
        self.assertIn("Could not find valid size for: 'UNKNOWN_SIZE'", str(ex))

    def test_generate_create_dict(self):
        args = {
            'size': 'S1270_8GB_2X1TBSATA_NORAID',
            'hostname': 'unicorn',
            'domain': 'giggles.woo',
            'location': 'wdc01',
            'os': 'UBUNTU_14_64',
            'port_speed': 10,
            'hourly': True,
            'extras': ['1_IPV6_ADDRESS'],
            'post_uri': 'http://example.com/script.php',
            'ssh_keys': [10],
        }

        expected = {
            'hardware': [{
                'domain': 'giggles.woo',
                'hostname': 'unicorn',
            }],
            'location': 'WASHINGTON_DC',
            'packageId': 200,
            'presetId': 64,
            'prices': [{'id': 21},
                       {'id': 420},
                       {'id': 906},
                       {'id': 37650},
                       {'id': 1800},
                       {'id': 272},
                       {'id': 17129}],
            'useHourlyPricing': True,
            'provisionScripts': ['http://example.com/script.php'],
            'sshKeys': [{'sshKeyIds': [10]}],
        }

        data = self.hardware._generate_create_dict(**args)

        self.assertEqual(expected, data)

    @mock.patch('SoftLayer.managers.hardware.HardwareManager'
                '._generate_create_dict')
    def test_verify_order(self, create_dict):
        create_dict.return_value = {'test': 1, 'verify': 1}

        self.hardware.verify_order(test=1, verify=1)

        create_dict.assert_called_once_with(test=1, verify=1)
        self.assert_called_with('SoftLayer_Product_Order', 'verifyOrder',
                                args=({'test': 1, 'verify': 1},))

    @mock.patch('SoftLayer.managers.hardware.HardwareManager'
                '._generate_create_dict')
    def test_place_order(self, create_dict):
        create_dict.return_value = {'test': 1, 'verify': 1}
        self.hardware.place_order(test=1, verify=1)

        create_dict.assert_called_once_with(test=1, verify=1)
        self.assert_called_with('SoftLayer_Product_Order', 'placeOrder',
                                args=({'test': 1, 'verify': 1},))

    def test_cancel_hardware_without_reason(self):
        mock = self.set_mock('SoftLayer_Hardware_Server', 'getObject')
        mock.return_value = {'id': 987, 'billingItem': {'id': 1234}}

        result = self.hardware.cancel_hardware(987)

        self.assertEqual(result, True)
        reasons = self.hardware.get_cancellation_reasons()
        args = (False, False, reasons['unneeded'], '')
        self.assert_called_with('SoftLayer_Billing_Item', 'cancelItem',
                                identifier=1234,
                                args=args)

    def test_cancel_hardware_with_reason_and_comment(self):
        mock = self.set_mock('SoftLayer_Hardware_Server', 'getObject')
        mock.return_value = {'id': 987, 'billingItem': {'id': 1234}}

        result = self.hardware.cancel_hardware(6327,
                                               reason='sales',
                                               comment='Test Comment')

        self.assertEqual(result, True)
        reasons = self.hardware.get_cancellation_reasons()
        args = (False, False, reasons['sales'], 'Test Comment')
        self.assert_called_with('SoftLayer_Billing_Item', 'cancelItem',
                                identifier=1234,
                                args=args)

    def test_cancel_hardware(self):

        result = self.hardware.cancel_hardware(6327)

        self.assertEqual(result, True)
        self.assert_called_with('SoftLayer_Billing_Item',
                                'cancelItem',
                                identifier=6327,
                                args=(False, False, 'No longer needed', ''))

    def test_cancel_hardware_no_billing_item(self):
        mock = self.set_mock('SoftLayer_Hardware_Server', 'getObject')
        mock.return_value = {'id': 987}

        ex = self.assertRaises(SoftLayer.SoftLayerError,
                               self.hardware.cancel_hardware,
                               6327)
        self.assertEqual("No billing item found for hardware",
                         str(ex))

    def test_change_port_speed_public(self):
        self.hardware.change_port_speed(2, True, 100)

        self.assert_called_with('SoftLayer_Hardware_Server',
                                'setPublicNetworkInterfaceSpeed',
                                identifier=2,
                                args=(100,))

    def test_change_port_speed_private(self):
        self.hardware.change_port_speed(2, False, 10)

        self.assert_called_with('SoftLayer_Hardware_Server',
                                'setPrivateNetworkInterfaceSpeed',
                                identifier=2,
                                args=(10,))

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


class HardwareHelperTests(testing.TestCase):
    def test_get_extra_price_id_no_items(self):
        ex = self.assertRaises(SoftLayer.SoftLayerError,
                               managers.hardware._get_extra_price_id,
                               [], 'test', True, None)
        self.assertEqual("Could not find valid price for extra option, 'test'",
                         str(ex))

    def test_get_default_price_id_item_not_first(self):
        items = [{
            'itemCategory': {'categoryCode': 'unknown', 'id': 325},
            'keyName': 'UNKNOWN',
            'prices': [{'accountRestrictions': [],
                        'currentPriceFlag': '',
                        'hourlyRecurringFee': '10.0',
                        'id': 1245172,
                        'recurringFee': '1.0'}],
        }]
        ex = self.assertRaises(SoftLayer.SoftLayerError,
                               managers.hardware._get_default_price_id,
                               items, 'unknown', True, None)
        self.assertEqual("Could not find valid price for 'unknown' option",
                         str(ex))

    def test_get_default_price_id_no_items(self):
        ex = self.assertRaises(SoftLayer.SoftLayerError,
                               managers.hardware._get_default_price_id,
                               [], 'test', True, None)
        self.assertEqual("Could not find valid price for 'test' option",
                         str(ex))

    def test_get_bandwidth_price_id_no_items(self):
        ex = self.assertRaises(SoftLayer.SoftLayerError,
                               managers.hardware._get_bandwidth_price_id,
                               [], hourly=True, no_public=False)
        self.assertEqual("Could not find valid price for bandwidth option",
                         str(ex))

    def test_get_os_price_id_no_items(self):
        ex = self.assertRaises(SoftLayer.SoftLayerError,
                               managers.hardware._get_os_price_id,
                               [], 'UBUNTU_14_64', None)
        self.assertEqual("Could not find valid price for os: 'UBUNTU_14_64'",
                         str(ex))

    def test_get_port_speed_price_id_no_items(self):
        ex = self.assertRaises(SoftLayer.SoftLayerError,
                               managers.hardware._get_port_speed_price_id,
                               [], 10, True, None)
        self.assertEqual("Could not find valid price for port speed: '10'",
                         str(ex))
