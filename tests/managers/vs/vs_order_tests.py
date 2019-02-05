"""
    SoftLayer.tests.managers.vs.vs_order_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    These tests deal with ordering in the VS manager.
    :license: MIT, see LICENSE for more details.

"""
import mock

import SoftLayer
from SoftLayer import fixtures
from SoftLayer import testing


class VSOrderTests(testing.TestCase):

    def set_up(self):
        self.vs = SoftLayer.VSManager(self.client)

    @mock.patch('SoftLayer.managers.vs.VSManager._generate_create_dict')
    def test_create_verify(self, create_dict):
        create_dict.return_value = {'test': 1, 'verify': 1}

        self.vs.verify_create_instance(test=1, verify=1, tags=['test', 'tags'])

        create_dict.assert_called_once_with(test=1, verify=1)
        self.assert_called_with('SoftLayer_Virtual_Guest',
                                'generateOrderTemplate',
                                args=({'test': 1, 'verify': 1},))

    def test_upgrade(self):
        # test single upgrade
        result = self.vs.upgrade(1, cpus=4, public=False)

        self.assertEqual(result, True)
        self.assert_called_with('SoftLayer_Product_Order', 'placeOrder')
        call = self.calls('SoftLayer_Product_Order', 'placeOrder')[0]
        order_container = call.args[0]
        self.assertEqual(order_container['prices'], [{'id': 1007}])
        self.assertEqual(order_container['virtualGuests'], [{'id': 1}])

    def test_upgrade_blank(self):
        # Now test a blank upgrade
        result = self.vs.upgrade(1)

        self.assertEqual(result, False)
        self.assertEqual(self.calls('SoftLayer_Product_Order', 'placeOrder'),
                         [])

    def test_upgrade_full(self):
        # Testing all parameters Upgrade
        result = self.vs.upgrade(1,
                                 cpus=4,
                                 memory=2,
                                 nic_speed=1000,
                                 public=True)

        self.assertEqual(result, True)
        self.assert_called_with('SoftLayer_Product_Order', 'placeOrder')
        call = self.calls('SoftLayer_Product_Order', 'placeOrder')[0]
        order_container = call.args[0]
        self.assertIn({'id': 1144}, order_container['prices'])
        self.assertIn({'id': 1133}, order_container['prices'])
        self.assertIn({'id': 1122}, order_container['prices'])
        self.assertEqual(order_container['virtualGuests'], [{'id': 1}])

    def test_upgrade_with_flavor(self):
        # Testing Upgrade with parameter preset
        result = self.vs.upgrade(1,
                                 preset="M1_64X512X100",
                                 nic_speed=1000,
                                 public=True)

        self.assertEqual(result, True)
        self.assert_called_with('SoftLayer_Product_Order', 'placeOrder')
        call = self.calls('SoftLayer_Product_Order', 'placeOrder')[0]
        order_container = call.args[0]
        self.assertEqual(799, order_container['presetId'])
        self.assertIn({'id': 1}, order_container['virtualGuests'])
        self.assertIn({'id': 1122}, order_container['prices'])
        self.assertEqual(order_container['virtualGuests'], [{'id': 1}])

    def test_upgrade_dedicated_host_instance(self):
        mock = self.set_mock('SoftLayer_Virtual_Guest', 'getUpgradeItemPrices')
        mock.return_value = fixtures.SoftLayer_Virtual_Guest.DEDICATED_GET_UPGRADE_ITEM_PRICES

        # test single upgrade
        result = self.vs.upgrade(1, cpus=4, public=False)

        self.assertEqual(result, True)
        self.assert_called_with('SoftLayer_Product_Order', 'placeOrder')
        call = self.calls('SoftLayer_Product_Order', 'placeOrder')[0]
        order_container = call.args[0]
        self.assertEqual(order_container['prices'], [{'id': 115566}])
        self.assertEqual(order_container['virtualGuests'], [{'id': 1}])

    def test_get_item_id_for_upgrade(self):
        item_id = 0
        package_items = self.client['Product_Package'].getItems(id=46)
        for item in package_items:
            if ((item['prices'][0]['categories'][0]['id'] == 3)
                    and (item.get('capacity') == '2')):
                item_id = item['prices'][0]['id']
                break
        self.assertEqual(1133, item_id)

    def test_get_package_items(self):
        self.vs._get_package_items()
        self.assert_called_with('SoftLayer_Product_Package', 'getItems')

    def test_get_price_id_for_upgrade(self):
        package_items = self.vs._get_package_items()

        price_id = self.vs._get_price_id_for_upgrade(package_items=package_items,
                                                     option='cpus',
                                                     value='4')
        self.assertEqual(1144, price_id)

    def test_get_price_id_for_upgrade_skips_location_price(self):
        package_items = self.vs._get_package_items()

        price_id = self.vs._get_price_id_for_upgrade(package_items=package_items,
                                                     option='cpus',
                                                     value='55')
        self.assertEqual(None, price_id)

    def test_get_price_id_for_upgrade_finds_nic_price(self):
        package_items = self.vs._get_package_items()

        price_id = self.vs._get_price_id_for_upgrade(package_items=package_items,
                                                     option='memory',
                                                     value='2')
        self.assertEqual(1133, price_id)

    def test_get_price_id_for_upgrade_finds_memory_price(self):
        package_items = self.vs._get_package_items()

        price_id = self.vs._get_price_id_for_upgrade(package_items=package_items,
                                                     option='nic_speed',
                                                     value='1000')
        self.assertEqual(1122, price_id)

    @mock.patch('SoftLayer.managers.vs.VSManager._generate_create_dict')
    def test_order_guest(self, create_dict):
        create_dict.return_value = {'test': 1, 'verify': 1}
        guest = {'test': 1, 'verify': 1, 'tags': ['First']}
        result = self.vs.order_guest(guest, test=False)
        create_dict.assert_called_once_with(test=1, verify=1)
        self.assertEqual(1234, result['orderId'])
        self.assert_called_with('SoftLayer_Virtual_Guest', 'generateOrderTemplate')
        self.assert_called_with('SoftLayer_Product_Order', 'placeOrder')
        self.assert_called_with('SoftLayer_Virtual_Guest', 'setTags', identifier=1234567)

    @mock.patch('SoftLayer.managers.vs.VSManager._generate_create_dict')
    def test_order_guest_verify(self, create_dict):
        create_dict.return_value = {'test': 1, 'verify': 1}
        guest = {'test': 1, 'verify': 1, 'tags': ['First']}
        result = self.vs.order_guest(guest, test=True)
        create_dict.assert_called_once_with(test=1, verify=1)
        self.assertEqual(1234, result['orderId'])
        self.assert_called_with('SoftLayer_Virtual_Guest', 'generateOrderTemplate')
        self.assert_called_with('SoftLayer_Product_Order', 'verifyOrder')

    @mock.patch('SoftLayer.managers.vs.VSManager._generate_create_dict')
    def test_order_guest_ipv6(self, create_dict):
        amock = self.set_mock('SoftLayer_Product_Package', 'getItems')
        amock.return_value = fixtures.SoftLayer_Product_Package.getItems_1_IPV6_ADDRESS
        create_dict.return_value = {'test': 1, 'verify': 1}
        guest = {'test': 1, 'verify': 1, 'tags': ['First'], 'ipv6': True}
        result = self.vs.order_guest(guest, test=True)
        self.assertEqual(1234, result['orderId'])
        self.assert_called_with('SoftLayer_Virtual_Guest', 'generateOrderTemplate')
        self.assert_called_with('SoftLayer_Product_Package', 'getItems', identifier=200)
        self.assert_called_with('SoftLayer_Product_Order', 'verifyOrder')
