"""
    SoftLayer.tests.managers.hardware_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import mock

import SoftLayer
from SoftLayer.managers import hardware
from SoftLayer import testing
from SoftLayer.testing import fixtures


class HardwareTests(testing.TestCase):

    def set_up(self):
        self.hardware = SoftLayer.HardwareManager(self.client)

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
        self.assertEqual(_id, [1000, 1001, 1002])

        _id = self.hardware._get_ids_from_ip('nope')
        self.assertEqual(_id, [])

        # Now simulate a private IP test
        mock = self.set_mock('SoftLayer_Account', 'getHardware')
        mock.side_effect = [[], [{'id': 99}]]

        _id = self.hardware._get_ids_from_ip('10.0.1.87')

        self.assertEqual(_id, [99])

    def test_resolve_ids_hostname(self):
        _id = self.hardware._get_ids_from_hostname('hardware-test1')
        self.assertEqual(_id, [1000, 1001, 1002])

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

    def test_get_bare_metal_create_options_returns_none_on_error(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        mock.return_value = [{
            'id': 0,
            'name': 'No Matching Instances',
            'description': 'Nothing'
        }]

        self.assertIsNone(self.hardware.get_bare_metal_create_options())

    def test_get_bare_metal_create_options(self):
        result = self.hardware.get_bare_metal_create_options()

        self.assertEqual(len(result['categories']['disk0']['items']), 2)
        self.assertEqual(len(result['categories']['disk1']['items']), 1)
        self.assertEqual(len(result['categories']['disk1']['items']), 1)
        self.assertEqual(len(result['categories']['disk_controller']['items']),
                         2)
        self.assertEqual(len(result['categories']['os']['items']), 11)
        self.assertEqual(len(result['categories']['port_speed']['items']), 5)
        self.assertEqual(len(result['categories']['ram']['items']), 2)
        self.assertEqual(len(result['categories']['random']['items']), 1)
        self.assertEqual(len(result['categories']['server']['items']), 2)
        self.assertEqual(len(result['categories']['server_core']['items']), 3)
        self.assertEqual(len(result['locations']), 1)

        self.assert_called_with('SoftLayer_Product_Package', 'getRegions',
                                identifier=50)

        self.assert_called_with('SoftLayer_Product_Package',
                                'getConfiguration',
                                identifier=50,
                                mask='mask[itemCategory[group]]')

        self.assert_called_with('SoftLayer_Product_Package', 'getCategories',
                                identifier=50)

    def test_generate_create_dict_with_all_bare_metal_options(self):
        args = {
            'server': 100,
            'hostname': 'unicorn',
            'domain': 'giggles.woo',
            'disks': [500],
            'location': 'Wyrmshire',
            'os': 200,
            'port_speed': 600,
            'bare_metal': True,
            'hourly': True,
            'public_vlan': 10234,
            'private_vlan': 20468,
        }

        expected = {
            'hardware': [
                {
                    'domain': 'giggles.woo',
                    'bareMetalInstanceFlag': True,
                    'hostname': 'unicorn',
                    'primaryBackendNetworkComponent':
                    {'networkVlan': {'id': 20468}},
                    'primaryNetworkComponent':
                    {'networkVlan': {'id': 10234}},
                }
            ],
            'prices': [
                {'id': 100},
                {'id': 500},
                {'id': 200},
                {'id': 600},
                {'id': 12000}
            ],
            'useHourlyPricing': True,
            'location': 'Wyrmshire', 'packageId': 50
        }

        data = self.hardware._generate_create_dict(**args)

        self.assertEqual(expected, data)

    def test_generate_create_dict_with_all_dedicated_server_options(self):
        args = {
            'server': 100,
            'hostname': 'unicorn',
            'domain': 'giggles.woo',
            'disks': [1000, 1000, 1000, 1000],
            'location': 'Wyrmshire',
            'os': 200,
            'port_speed': 600,
            'bare_metal': False,
            'package_id': 13,
            'ram': 1400,
            'disk_controller': 1500,
            'ssh_keys': [3000, 3001],
            'public_vlan': 10234,
            'private_vlan': 20468,
            'post_uri': 'http://somescript.foo/myscript.sh',
        }

        expected = {
            'hardware': [
                {
                    'domain': 'giggles.woo',
                    'bareMetalInstanceFlag': False,
                    'hostname': 'unicorn',
                    'primaryBackendNetworkComponent':
                    {'networkVlan': {'id': 20468}},
                    'primaryNetworkComponent':
                    {'networkVlan': {'id': 10234}},
                }
            ],
            'prices': [
                {'id': 100},
                {'id': 1000},
                {'id': 1000},
                {'id': 1000},
                {'id': 1000},
                {'id': 200},
                {'id': 600},
                {'id': 1400},
                {'id': 1500}],
            'sshKeys': [{'sshKeyIds': [3000, 3001]}],
            'location': 'Wyrmshire', 'packageId': 13,
            'provisionScripts': ['http://somescript.foo/myscript.sh'],
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

    def test_cancel_metal_immediately(self):

        result = self.hardware.cancel_metal(6327, immediate=True)

        self.assertEqual(result, True)
        self.assert_called_with('SoftLayer_Billing_Item', 'cancelService',
                                identifier=6327)

    def test_cancel_metal_on_anniversary(self):

        result = self.hardware.cancel_metal(6327, False)

        self.assertEqual(result, True)
        self.assert_called_with('SoftLayer_Billing_Item',
                                'cancelServiceOnAnniversaryDate',
                                identifier=6327)

    def test_cancel_hardware_without_reason(self):
        mock = self.set_mock('SoftLayer_Hardware_Server', 'getObject')
        mock.return_value = {'id': 987, 'bareMetalInstanceFlag': False}

        result = self.hardware.cancel_hardware(987)

        self.assertEqual(result,
                         fixtures.SoftLayer_Ticket.createCancelServerTicket)
        reasons = self.hardware.get_cancellation_reasons()
        args = (987, reasons['unneeded'], '', True, 'HARDWARE')
        self.assert_called_with('SoftLayer_Ticket', 'createCancelServerTicket',
                                args=args)

    def test_cancel_hardware_with_reason_and_comment(self):
        mock = self.set_mock('SoftLayer_Hardware_Server', 'getObject')
        mock.return_value = {'id': 987, 'bareMetalInstanceFlag': False}

        result = self.hardware.cancel_hardware(987, 'sales', 'Test Comment')

        self.assertEqual(result,
                         fixtures.SoftLayer_Ticket.createCancelServerTicket)
        reasons = self.hardware.get_cancellation_reasons()
        args = (987, reasons['sales'], 'Test Comment', True, 'HARDWARE')
        self.assert_called_with('SoftLayer_Ticket', 'createCancelServerTicket',
                                args=args)

    def test_cancel_hardware_on_bmc(self):

        result = self.hardware.cancel_hardware(6327)

        self.assertEqual(result, True)
        self.assert_called_with('SoftLayer_Billing_Item',
                                'cancelServiceOnAnniversaryDate',
                                identifier=6327)

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

    def test_get_available_dedicated_server_packages(self):
        self.hardware.get_available_dedicated_server_packages()

        _filter = {
            'type': {
                'keyName': {
                    'operation': 'in',
                    'options': [{
                        'name': 'data',
                        'value': ['BARE_METAL_CPU',
                                  'BARE_METAL_CORE']
                    }]
                }
            }
        }
        self.assert_called_with('SoftLayer_Product_Package', 'getAllObjects',
                                filter=_filter,
                                mask='id,name,description,type,isActive')

    def test_get_server_packages_with_ordering_manager_provided(self):
        self.hardware = SoftLayer.HardwareManager(
            self.client, SoftLayer.OrderingManager(self.client))
        self.test_get_available_dedicated_server_packages()

    def test_get_dedicated_server_options(self):
        result = self.hardware.get_dedicated_server_create_options(13)

        self.assertEqual(len(result['categories']['disk0']['items']), 2)
        self.assertEqual(len(result['categories']['disk1']['items']), 1)
        self.assertEqual(len(result['categories']['disk1']['items']), 1)
        self.assertEqual(len(result['categories']['disk_controller']['items']),
                         2)
        self.assertEqual(len(result['categories']['os']['items']), 11)
        self.assertEqual(len(result['categories']['port_speed']['items']), 5)
        self.assertEqual(len(result['categories']['ram']['items']), 2)
        self.assertEqual(len(result['categories']['random']['items']), 1)
        self.assertEqual(len(result['categories']['server']['items']), 2)
        self.assertEqual(len(result['categories']['server_core']['items']), 3)
        self.assertEqual(len(result['locations']), 1)

        self.assert_called_with('SoftLayer_Product_Package', 'getRegions',
                                identifier=13)

        self.assert_called_with('SoftLayer_Product_Package',
                                'getConfiguration',
                                identifier=13,
                                mask='mask[itemCategory[group]]')

        self.assert_called_with('SoftLayer_Product_Package', 'getCategories',
                                identifier=13)

    def test_get_default_value_returns_none_for_unknown_category(self):
        package_options = {'categories': ['Cat1', 'Cat2']}

        self.assertEqual(None, hardware.get_default_value(package_options,
                                                          'Unknown Category'))

    def test_get_default_value(self):
        price_id = 9876
        package_options = {'categories':
                           {'Cat1': {
                               'items': [{'setup_fee': 0,
                                          'recurring_fee': 0,
                                          'hourly_recurring_fee': 0,
                                          'one_time_fee': 0,
                                          'labor_fee': 0,
                                          'price_id': price_id}]
                           }}}

        self.assertEqual(price_id,
                         hardware.get_default_value(package_options, 'Cat1'))

    def test_get_default_value_none_free(self):
        package_options = {'categories': {}}
        self.assertEqual(None,
                         hardware.get_default_value(package_options, 'Cat1'))

        package_options = {'categories':
                           {'Cat1': {
                               'items': [{'setup_fee': 10,
                                          'recurring_fee': 0,
                                          'hourly_recurring_fee': 0,
                                          'one_time_fee': 0,
                                          'labor_fee': 0,
                                          'price_id': 1234}]
                           }}}
        self.assertEqual(None,
                         hardware.get_default_value(package_options, 'Cat1'))

    def test_get_default_value_hourly(self):
        package_options = {'categories':
                           {'Cat1': {
                               'items': [{'setup_fee': 0,
                                          'recurring_fee': 0,
                                          'hourly_recurring_fee': None,
                                          'one_time_fee': 0,
                                          'labor_fee': 0,
                                          'price_id': 1234},
                                         {'setup_fee': 0,
                                          'recurring_fee': None,
                                          'hourly_recurring_fee': 0,
                                          'one_time_fee': 0,
                                          'labor_fee': 0,
                                          'price_id': 4321}]
                           }}}
        result = hardware.get_default_value(package_options, 'Cat1',
                                            hourly=True)
        self.assertEqual(4321, result)

    def test_get_default_value_monthly(self):
        package_options = {'categories':
                           {'Cat1': {
                               'items': [{'setup_fee': 0,
                                          'recurring_fee': None,
                                          'hourly_recurring_fee': 0,
                                          'one_time_fee': 0,
                                          'labor_fee': 0,
                                          'price_id': 4321},
                                         {'setup_fee': 0,
                                          'recurring_fee': 0,
                                          'hourly_recurring_fee': None,
                                          'one_time_fee': 0,
                                          'labor_fee': 0,
                                          'price_id': 1234}]
                           }}}
        result = hardware.get_default_value(package_options, 'Cat1',
                                            hourly=False)
        self.assertEqual(1234, result)

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
        # Test rescue environment
        restult = self.hardware.rescue(1234)

        self.assertEqual(restult, True)
        self.assert_called_with('SoftLayer_Hardware_Server',
                                'bootToRescueLayer',
                                identifier=1234)
