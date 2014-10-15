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
        self.client = testing.FixtureClient()
        self.hardware = SoftLayer.HardwareManager(self.client)

    def test_list_hardware(self):
        mcall = mock.call(mask=mock.ANY, filter={})

        results = self.hardware.list_hardware()
        self.client['Account'].getHardware.assert_has_calls(mcall)
        self.assertEqual(results, fixtures.Account.getHardware)

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
        self.client['Account'].getHardware.assert_has_calls(mock.call(
            filter={
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
            },
            mask=mock.ANY,
        ))
        self.assertEqual(results, fixtures.Account.getHardware)

    def test_resolve_ids_ip(self):
        _id = self.hardware._get_ids_from_ip('172.16.1.100')
        self.assertEqual(_id, [1000, 1001, 1002])

        _id = self.hardware._get_ids_from_ip('nope')
        self.assertEqual(_id, [])

        # Now simulate a private IP test
        self.client['Account'].getHardware.side_effect = [[], [{'id': 99}]]
        _id = self.hardware._get_ids_from_ip('10.0.1.87')
        self.assertEqual(_id, [99])

    def test_resolve_ids_hostname(self):
        _id = self.hardware._get_ids_from_hostname('hardware-test1')
        self.assertEqual(_id, [1000, 1001, 1002])

    def test_get_hardware(self):
        result = self.hardware.get_hardware(1000)

        self.client['Hardware_Server'].getObject.assert_called_once_with(
            id=1000, mask=mock.ANY)
        self.assertEqual(fixtures.Hardware_Server.getObject, result)

    def test_reload(self):
        post_uri = 'http://test.sftlyr.ws/test.sh'
        self.hardware.reload(1, post_uri=post_uri, ssh_keys=[1701])
        f = self.client['Hardware_Server'].reloadOperatingSystem
        f.assert_called_once_with('FORCE',
                                  {'customProvisionScriptUri': post_uri,
                                   'sshKeyIds': [1701]}, id=1)

    def test_get_bare_metal_create_options_returns_none_on_error(self):
        self.client['Product_Package'].getAllObjects.return_value = [
            {'name': 'No Matching Instances', 'id': 0,
             'description': 'Nothing'}]

        self.assertIsNone(self.hardware.get_bare_metal_create_options())

    def test_get_bare_metal_create_options(self):
        package_id = 50
        self.hardware.get_bare_metal_create_options()

        f1 = self.client['Product_Package'].getRegions
        f1.assert_called_once_with(id=package_id)

        f2 = self.client['Product_Package'].getConfiguration
        f2.assert_called_once_with(id=package_id,
                                   mask='mask[itemCategory[group]]')

        f3 = self.client['Product_Package'].getCategories
        f3.assert_called_once_with(id=package_id)

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
        f = self.client['Product_Order'].verifyOrder
        f.assert_called_once_with({'test': 1, 'verify': 1})

    @mock.patch('SoftLayer.managers.hardware.HardwareManager'
                '._generate_create_dict')
    def test_place_order(self, create_dict):
        create_dict.return_value = {'test': 1, 'verify': 1}
        self.hardware.place_order(test=1, verify=1)
        create_dict.assert_called_once_with(test=1, verify=1)
        f = self.client['Product_Order'].placeOrder
        f.assert_called_once_with({'test': 1, 'verify': 1})

    def test_cancel_metal_immediately(self):
        b_id = 6327

        result = self.hardware.cancel_metal(b_id, immediate=True)
        f = self.client['Billing_Item'].cancelService
        f.assert_called_once_with(id=b_id)
        self.assertEqual(result, fixtures.Billing_Item.cancelService)

    def test_cancel_metal_on_anniversary(self):
        b_id = 6327

        result = self.hardware.cancel_metal(b_id, False)
        f = self.client['Billing_Item'].cancelServiceOnAnniversaryDate
        f.assert_called_once_with(id=b_id)
        self.assertEqual(result,
                         fixtures.Billing_Item.cancelServiceOnAnniversaryDate)

    def test_cancel_hardware_without_reason(self):
        hw_id = 987
        self.client['Hardware_Server'].getObject.return_value = {
            'id': hw_id,
            'bareMetalInstanceFlag': False,
        }
        result = self.hardware.cancel_hardware(hw_id)

        reasons = self.hardware.get_cancellation_reasons()
        f = self.client['Ticket'].createCancelServerTicket
        f.assert_called_once_with(hw_id, reasons['unneeded'], '', True,
                                  'HARDWARE')
        self.assertEqual(result,
                         fixtures.Ticket.createCancelServerTicket)

    def test_cancel_hardware_with_reason_and_comment(self):
        hw_id = 987
        reason = 'sales'
        comment = 'Test Comment'

        self.client['Hardware_Server'].getObject.return_value = {
            'id': hw_id,
            'bareMetalInstanceFlag': False,
        }

        self.hardware.cancel_hardware(hw_id, reason, comment)

        reasons = self.hardware.get_cancellation_reasons()

        f = self.client['Ticket'].createCancelServerTicket
        f.assert_called_once_with(hw_id, reasons[reason], comment, True,
                                  'HARDWARE')

    def test_cancel_hardware_on_bmc(self):
        hw_id = 6327

        result = self.hardware.cancel_hardware(hw_id)
        f = self.client['Billing_Item'].cancelServiceOnAnniversaryDate
        f.assert_called_once_with(id=hw_id)
        self.assertEqual(result,
                         fixtures.Billing_Item.cancelServiceOnAnniversaryDate)

    def test_change_port_speed_public(self):
        hw_id = 1
        speed = 100
        self.hardware.change_port_speed(hw_id, True, speed)

        f = self.client['Hardware_Server'].setPublicNetworkInterfaceSpeed
        f.assert_called_once_with(speed, id=hw_id)

    def test_change_port_speed_private(self):
        hw_id = 2
        speed = 10
        self.hardware.change_port_speed(hw_id, False, speed)

        f = self.client['Hardware_Server'].setPrivateNetworkInterfaceSpeed
        f.assert_called_once_with(speed, id=hw_id)

    def test_get_available_dedicated_server_packages(self):
        self.hardware.get_available_dedicated_server_packages()

        filter_mock = {
            'type': {
                'keyName': {
                    'operation': 'in',
                    'options': [{
                        'name': 'data',
                        'value': ['BARE_METAL_CPU',
                                  'BARE_METAL_CORE',
                                  'BARE_METAL_CPU_FAST_PROVISION']
                    }]
                }
            }
        }
        f = self.client['Product_Package'].getAllObjects
        f.assert_has_calls([mock.call(mask='id,name,description,type,isActive',
                                      filter=filter_mock)])

    def test_get_server_packages_with_ordering_manager_provided(self):
        self.hardware = SoftLayer.HardwareManager(
            self.client, SoftLayer.OrderingManager(self.client))
        self.test_get_available_dedicated_server_packages()

    def test_get_dedicated_server_options(self):
        package_id = 13
        self.hardware.get_dedicated_server_create_options(package_id)

        f1 = self.client['Product_Package'].getRegions
        f1.assert_called_once_with(id=package_id)

        f2 = self.client['Product_Package'].getConfiguration
        f2.assert_called_once_with(id=package_id,
                                   mask='mask[itemCategory[group]]')

        f3 = self.client['Product_Package'].getCategories
        f3.assert_called_once_with(id=package_id)

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

    def test_edit(self):
        # Test editing user data
        self.hardware.edit(100, userdata='my data')

        service = self.client['Hardware_Server']
        service.setUserMetadata.assert_called_once_with(['my data'], id=100)

        # Now test a blank edit
        self.assertTrue(self.hardware.edit, 100)

        # Finally, test a full edit
        args = {
            'hostname': 'new-host',
            'domain': 'new.sftlyr.ws',
            'notes': 'random notes',
        }

        self.hardware.edit(100, **args)
        service.editObject.assert_called_once_with(args, id=100)

    def test_rescue(self):
        # Test rescue environment
        hardware_id = 1234
        self.hardware.rescue(hardware_id)

        service = self.client['Hardware_Server']
        f = service.bootToRescueLayer
        f.assert_called_once_with(id=hardware_id)
