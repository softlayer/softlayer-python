"""
    SoftLayer.tests.managers.hardware_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
    :license: BSD, see LICENSE for more details.
"""
from SoftLayer import HardwareManager

try:
    import unittest2 as unittest
except ImportError:
    import unittest  # NOQA
from mock import MagicMock, ANY, call, patch


class HardwareTests(unittest.TestCase):

    def setUp(self):
        self.client = MagicMock()
        self.hardware = HardwareManager(self.client)

    def test_list_hardware(self):
        mcall = call(mask=ANY, filter={})
        service = self.client.__getitem__()

        self.hardware.list_hardware()
        service.getHardware.assert_has_calls(mcall)

    def test_list_hardware_with_filters(self):
        self.hardware.list_hardware(
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
        service = self.client.__getitem__()
        service.getHardware.assert_has_calls(call(
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
                    'processorCoreAmount': {'operation': 2},
                    'hostname': {'operation': '_= hostname'},
                    'primaryIpAddress': {'operation': '_= 1.2.3.4'},
                    'networkComponents': {'maxSpeed': {'operation': 100}},
                    'primaryBackendIpAddress': {'operation': '_= 4.3.2.1'}}
            },
            mask=ANY,
        ))

    def test_resolve_ids_ip(self):
        self.client.__getitem__().getHardware.return_value = [{'id': '1234'}]
        _id = self.hardware._get_ids_from_ip('1.2.3.4')
        self.assertEqual(_id, ['1234'])

        self.client.__getitem__().getHardware.side_effect = \
            [[], [{'id': '4321'}]]
        _id = self.hardware._get_ids_from_ip('4.3.2.1')
        self.assertEqual(_id, ['4321'])

        _id = self.hardware._get_ids_from_ip('nope')
        self.assertEqual(_id, [])

    def test_resolve_ids_hostname(self):
        self.client.__getitem__().getHardware.return_value = [{'id': '1234'}]
        _id = self.hardware._get_ids_from_hostname('hostname')
        self.assertEqual(_id, ['1234'])

    def test_get_hardware(self):
        self.client.__getitem__().getObject.return_value = {
            'hourlyVirtualGuests': "this is unique"}
        self.hardware.get_hardware(1)
        self.client.__getitem__().getObject.assert_called_once_with(
            id=1, mask=ANY)

    def test_reload(self):
        self.hardware.reload(id=1)
        f = self.client.__getitem__().reloadCurrentOperatingSystemConfiguration
        f.assert_called_once_with('FORCE', id=1)

    def test_get_bare_metal_create_options_returns_none_on_error(self):
        self.client['Product_Package'].getAllObjects.return_value = [
            {'name': 'No Matching Instances', 'id': 0}]

        self.assertIsNone(self.hardware.get_bare_metal_create_options())

    def test_get_bare_metal_create_options(self):
        package_id = 50

        self.client['Product_Package'].getAllObjects.return_value = [
            {'name': 'Bare Metal Instance', 'id': package_id}]

        self.client['Product_Package'].getRegions.return_value = [{
            'location': {
                'locationPackageDetails': [{
                    'deliveryTimeInformation': 'Typically 2-4 hours',
                }],
            },
            'keyname': 'RANDOM_LOCATION',
            'description': 'Random unit testing location',
        }]

        self.client['Product_Package'].getConfiguration.return_value = [{
            'itemCategory': {
                'categoryCode': 'random',
                'name': 'Random Category',
            },
            'sort': 0,
            'orderStepId': 1,
            'isRequired': 0,
        }]

        prices = [{'sort': 0, 'id': 999}]
        self.client['Product_Package'].getItems.return_value = [{
            'itemCategory': {
                'categoryCode': 'random2',
                'name': 'Another Category',
            },
            'id': 1000,
            'description': 'Astronaut Sloths',
            'prices': prices,
            'capacity': 0,
        }]
        self.hardware.get_bare_metal_create_options()

        f1 = self.client['Product_Package'].getRegions
        f1.assert_called_once_with(id=package_id)

        f2 = self.client['Product_Package'].getConfiguration
        f2.assert_called_once_with(id=package_id, mask='mask[itemCategory]')

        f3 = self.client['Product_Package'].getItems
        f3.assert_called_once_with(id=package_id, mask='mask[itemCategory]')

    def test_generate_create_dict_with_all_options(self):
        package_id = 50

        self.client['Product_Package'].getAllObjects.return_value = [
            {'name': 'Bare Metal Instance', 'id': package_id}]

        args = {
            'server_core': 100,
            'hourly': False,
            'hostname': 'unicorn',
            'domain': 'giggles.woo',
            'disk0': 500,
            'location': 'Wyrmshire',
            'os': 200,
            'image_id': None,
            'pri_ip_addresses': 300,
            'bandwidth': 400,
            'userdata': None,
            'monitoring': 500,
            'port_speed': 600,
            'vulnerability_scanner': 700,
            'response': 800,
            'vpn_management': 900,
            'remote_management': 1000,
            'notification': 1100,
            'bare_metal': True,
            'database': 1200,
        }

        assert_data = {
            'hardware': [{
                'bareMetalInstanceFlag': args['bare_metal'],
                'hostname': args['hostname'],
                'domain': args['domain'],
            }],
            'location': args['location'],
            'packageId': package_id,
            'prices': [
                {'id': args['server_core']},
                {'id': args['disk0']},
                {'id': args['os']},
                {'id': args['pri_ip_addresses']},
                {'id': args['bandwidth']},
                {'id': args['monitoring']},
                {'id': args['port_speed']},
                {'id': args['vulnerability_scanner']},
                {'id': args['response']},
                {'id': args['vpn_management']},
                {'id': args['remote_management']},
                {'id': args['notification']},
            ],
        }

        data = self.hardware._generate_create_dict(**args)

        self.assertEqual(data, assert_data)

    @patch('SoftLayer.managers.hardware.HardwareManager._generate_create_dict')
    def test_verify_order(self, create_dict):
        create_dict.return_value = {'test': 1, 'verify': 1}
        self.hardware.verify_order(test=1, verify=1)
        create_dict.assert_called_once_with(test=1, verify=1)
        f = self.client['Product_Order'].verifyOrder
        f.assert_called_once_with({'test': 1, 'verify': 1})

    @patch('SoftLayer.managers.hardware.HardwareManager._generate_create_dict')
    def test_place_order(self, create_dict):
        create_dict.return_value = {'test': 1, 'verify': 1}
        self.hardware.place_order(test=1, verify=1)
        create_dict.assert_called_once_with(test=1, verify=1)
        f = self.client['Product_Order'].placeOrder
        f.assert_called_once_with({'test': 1, 'verify': 1})

    def test_cancel_metal_immediately(self):
        b_id = 5678
        self.client.__getitem__().getObject.return_value = {'id': '1234',
                                                            'billingItem': {
                                                                'id': b_id,
                                                            }}
        self.hardware.cancel_metal(b_id, True)
        f = self.client['Billing_Item'].cancelService
        f.assert_called_once_with(id=b_id)

    def test_cancel_metal_on_anniversary(self):
        b_id = 5678
        self.client.__getitem__().getObject.return_value = {'id': '1234',
                                                            'billingItem': {
                                                                'id': b_id,
                                                            }}
        self.hardware.cancel_metal(b_id, False)
        f = self.client['Billing_Item'].cancelServiceOnAnniversaryDate
        f.assert_called_once_with(id=b_id)

    def test_cancel_hardware_without_reason(self):
        hw_id = 987

        self.hardware.cancel_hardware(hw_id)

        reasons = self.hardware.get_cancellation_reasons()

        f = self.client['Ticket'].createCancelServerTicket
        f.assert_called_once_with(hw_id, reasons['unneeded'], '', True,
                                  'HARDWARE')

    def test_cancel_hardware_with_reason_and_comment(self):
        hw_id = 987
        reason = 'sales'
        comment = 'Test Comment'

        self.hardware.cancel_hardware(hw_id, reason, comment)

        reasons = self.hardware.get_cancellation_reasons()

        f = self.client['Ticket'].createCancelServerTicket
        f.assert_called_once_with(hw_id, reasons[reason], comment, True,
                                  'HARDWARE')

    def test_change_port_speed_public(self):
        hw_id = 1
        speed = 100
        self.hardware.change_port_speed(hw_id, 'eth1', speed)

        service = self.client['Hardware_Server']
        f = service.setPublicNetworkInterfaceSpeed
        f.assert_called_once_with(speed, id=hw_id)

    def test_change_port_speed_private(self):
        hw_id = 2
        speed = 10
        self.hardware.change_port_speed(hw_id, 'eth0', speed)

        service = self.client['Hardware_Server']
        f = service.setPrivateNetworkInterfaceSpeed
        f.assert_called_once_with(speed, id=hw_id)

    def test_change_port_speed_errors_with_invalid_nic(self):
       self.assertRaises(ValueError, self.hardware.change_port_speed, 3, 'mgmt0', 100)
