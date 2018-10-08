"""
    SoftLayer.tests.CLI.modules.order_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    :license: MIT, see LICENSE for more details.
"""
import json

from SoftLayer import testing


class OrderTests(testing.TestCase):
    def test_category_list(self):
        cat1 = {'itemCategory': {'name': 'cat1', 'categoryCode': 'code1'}, 'isRequired': 1}
        cat2 = {'itemCategory': {'name': 'cat2', 'categoryCode': 'code2'}, 'isRequired': 0}
        p_mock = self.set_mock('SoftLayer_Product_Package', 'getConfiguration')
        p_mock.return_value = [cat1, cat2]

        result = self.run_command(['order', 'category-list', 'package'])

        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Product_Package', 'getConfiguration')
        self.assertEqual([{'name': 'cat1',
                           'categoryCode': 'code1',
                           'isRequired': 'Y'},
                          {'name': 'cat2',
                           'categoryCode': 'code2',
                           'isRequired': 'N'}],
                         json.loads(result.output))

    def test_item_list(self):
        category = {'categoryCode': 'testing'}
        item1 = {'keyName': 'item1', 'description': 'description1', 'itemCategory': category}
        item2 = {'keyName': 'item2', 'description': 'description2', 'itemCategory': category}
        p_mock = self.set_mock('SoftLayer_Product_Package', 'getItems')
        p_mock.return_value = [item1, item2]

        result = self.run_command(['order', 'item-list', 'package'])

        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Product_Package', 'getItems')
        expected_results = [{'category': 'testing',
                             'keyName': 'item1',
                             'description': 'description1'},
                            {'category': 'testing',
                             'keyName': 'item2',
                             'description': 'description2'}]
        self.assertEqual(expected_results, json.loads(result.output))

    def test_package_list(self):
        p_mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        p_mock.return_value = _get_all_packages()
        _filter = {'type': {'keyName': {'operation': '!= BLUEMIX_SERVICE'}}}

        result = self.run_command(['order', 'package-list'])

        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Product_Package', 'getAllObjects', filter=_filter)
        expected_results = [{'id': 1, 'name': 'package1', 'keyName': 'PACKAGE1', 'type': 'BARE_METAL_CPU'},
                            {'id': 2, 'name': 'package2', 'keyName': 'PACKAGE2', 'type': 'BARE_METAL_CPU'}]
        self.assertEqual(expected_results, json.loads(result.output))

    def test_package_list_keyword(self):
        p_mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        p_mock.return_value = _get_all_packages()

        _filter = {'type': {'keyName': {'operation': '!= BLUEMIX_SERVICE'}}}
        _filter['name'] = {'operation': '*= package1'}
        result = self.run_command(['order', 'package-list', '--keyword', 'package1'])

        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Product_Package', 'getAllObjects', filter=_filter)
        expected_results = [{'id': 1, 'name': 'package1', 'keyName': 'PACKAGE1', 'type': 'BARE_METAL_CPU'},
                            {'id': 2, 'name': 'package2', 'keyName': 'PACKAGE2', 'type': 'BARE_METAL_CPU'}]
        self.assertEqual(expected_results, json.loads(result.output))

    def test_package_list_type(self):
        p_mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        p_mock.return_value = _get_all_packages()

        _filter = {'type': {'keyName': {'operation': 'BARE_METAL_CPU'}}}
        result = self.run_command(['order', 'package-list', '--package_type', 'BARE_METAL_CPU'])

        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Product_Package', 'getAllObjects', filter=_filter)
        expected_results = [{'id': 1, 'name': 'package1', 'keyName': 'PACKAGE1', 'type': 'BARE_METAL_CPU'},
                            {'id': 2, 'name': 'package2', 'keyName': 'PACKAGE2', 'type': 'BARE_METAL_CPU'}]
        self.assertEqual(expected_results, json.loads(result.output))

    def test_place(self):
        order_date = '2017-04-04 07:39:20'
        order = {'orderId': 1234, 'orderDate': order_date, 'placedOrder': {'status': 'APPROVED'}}
        verify_mock = self.set_mock('SoftLayer_Product_Order', 'verifyOrder')
        place_mock = self.set_mock('SoftLayer_Product_Order', 'placeOrder')
        items_mock = self.set_mock('SoftLayer_Product_Package', 'getItems')

        verify_mock.return_value = self._get_verified_order_return()
        place_mock.return_value = order
        items_mock.return_value = self._get_order_items()

        result = self.run_command(['-y', 'order', 'place', 'package', 'DALLAS13', 'ITEM1',
                                   '--complex-type', 'SoftLayer_Container_Product_Order_Thing'])

        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Product_Order', 'placeOrder')
        self.assertEqual({'id': 1234,
                          'created': order_date,
                          'status': 'APPROVED'},
                         json.loads(result.output))

    def test_place_quote(self):
        order_date = '2018-04-04 07:39:20'
        expiration_date = '2018-05-04 07:39:20'
        quote_name = 'foobar'
        order = {'orderDate': order_date,
                 'quote': {
                     'id': 1234,
                     'name': quote_name,
                     'expirationDate': expiration_date,
                     'status': 'PENDING'
                 }}
        place_quote_mock = self.set_mock('SoftLayer_Product_Order', 'placeQuote')
        items_mock = self.set_mock('SoftLayer_Product_Package', 'getItems')

        place_quote_mock.return_value = order
        items_mock.return_value = self._get_order_items()

        result = self.run_command(['order', 'place-quote', '--name', 'foobar', 'package', 'DALLAS13',
                                   'ITEM1', '--complex-type', 'SoftLayer_Container_Product_Order_Thing'])

        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Product_Order', 'placeQuote')
        self.assertEqual({'id': 1234,
                          'name': quote_name,
                          'created': order_date,
                          'expires': expiration_date,
                          'status': 'PENDING'},
                         json.loads(result.output))

    def test_verify_hourly(self):
        order_date = '2017-04-04 07:39:20'
        order = {'orderId': 1234, 'orderDate': order_date,
                 'placedOrder': {'status': 'APPROVED'}}
        verify_mock = self.set_mock('SoftLayer_Product_Order', 'verifyOrder')
        items_mock = self.set_mock('SoftLayer_Product_Package', 'getItems')

        order = self._get_verified_order_return()
        verify_mock.return_value = order
        items_mock.return_value = self._get_order_items()

        result = self.run_command(['order', 'place', '--billing', 'hourly', '--verify',
                                   '--complex-type', 'SoftLayer_Container_Product_Order_Thing',
                                   'package', 'DALLAS13', 'ITEM1', 'ITEM2'])

        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Product_Order', 'verifyOrder')
        expected_results = []

        for price in order['orderContainers'][0]['prices']:
            expected_results.append({'keyName': price['item']['keyName'],
                                     'description': price['item']['description'],
                                     'cost': price['hourlyRecurringFee']})

        self.assertEqual(expected_results,
                         json.loads(result.output))

    def test_verify_monthly(self):
        order_date = '2017-04-04 07:39:20'
        order = {'orderId': 1234, 'orderDate': order_date,
                 'placedOrder': {'status': 'APPROVED'}}
        verify_mock = self.set_mock('SoftLayer_Product_Order', 'verifyOrder')
        items_mock = self.set_mock('SoftLayer_Product_Package', 'getItems')

        order = self._get_verified_order_return()
        verify_mock.return_value = order
        items_mock.return_value = self._get_order_items()

        result = self.run_command(['order', 'place', '--billing', 'monthly', '--verify',
                                   '--complex-type', 'SoftLayer_Container_Product_Order_Thing',
                                   'package', 'DALLAS13', 'ITEM1', 'ITEM2'])

        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Product_Order', 'verifyOrder')
        expected_results = []

        for price in order['orderContainers'][0]['prices']:
            expected_results.append({'keyName': price['item']['keyName'],
                                     'description': price['item']['description'],
                                     'cost': price['recurringFee']})

        self.assertEqual(expected_results,
                         json.loads(result.output))

    def test_preset_list(self):
        active_preset1 = {'name': 'active1', 'keyName': 'PRESET1',
                          'description': 'description1'}
        active_preset2 = {'name': 'active2', 'keyName': 'PRESET2',
                          'description': 'description2'}
        acc_preset = {'name': 'account1', 'keyName': 'PRESET3',
                      'description': 'description3'}
        active_mock = self.set_mock('SoftLayer_Product_Package', 'getActivePresets')
        account_mock = self.set_mock('SoftLayer_Product_Package',
                                     'getAccountRestrictedActivePresets')
        active_mock.return_value = [active_preset1, active_preset2]
        account_mock.return_value = [acc_preset]

        result = self.run_command(['order', 'preset-list', 'package'])

        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Product_Package', 'getActivePresets')
        self.assert_called_with('SoftLayer_Product_Package',
                                'getAccountRestrictedActivePresets')
        self.assertEqual([{'name': 'active1',
                           'keyName': 'PRESET1',
                           'description': 'description1'},
                          {'name': 'active2',
                           'keyName': 'PRESET2',
                           'description': 'description2'},
                          {'name': 'account1',
                           'keyName': 'PRESET3',
                           'description': 'description3'}],
                         json.loads(result.output))

    def test_location_list(self):
        result = self.run_command(['order', 'package-locations', 'package'])
        self.assert_no_fail(result)
        expected_results = [
            {'id': 2017603, 'dc': 'wdc07', 'description': 'WDC07 - Washington, DC', 'keyName': 'WASHINGTON07'}
        ]
        print("FUCK")
        print(result.output)
        self.assertEqual(expected_results, json.loads(result.output))

    def _get_order_items(self):
        item1 = {'keyName': 'ITEM1', 'description': 'description1',
                 'itemCategory': {'categoryCode': 'cat1'},
                 'prices': [{'id': 1111, 'locationGroupId': None,
                             'categories': [{'categoryCode': 'cat1'}]}]}
        item2 = {'keyName': 'ITEM2', 'description': 'description2',
                 'itemCategory': {'categoryCode': 'cat2'},
                 'prices': [{'id': 2222, 'locationGroupId': None,
                             'categories': [{'categoryCode': 'cat2'}]}]}

        return [item1, item2]

    def _get_verified_order_return(self):
        item1, item2 = self._get_order_items()
        price1 = {'item': item1, 'hourlyRecurringFee': '0.04',
                  'recurringFee': '120'}
        price2 = {'item': item2, 'hourlyRecurringFee': '0.05',
                  'recurringFee': '150'}
        return {'orderContainers': [{'prices': [price1, price2]}]}


def _get_all_packages():
    package_type = {'keyName': 'BARE_METAL_CPU'}
    all_packages = [
        {'id': 1, 'name': 'package1', 'keyName': 'PACKAGE1', 'type': package_type, 'isActive': 1},
        {'id': 2, 'name': 'package2', 'keyName': 'PACKAGE2', 'type': package_type, 'isActive': 1},
        {'id': 3, 'name': 'package2', 'keyName': 'PACKAGE2', 'type': package_type, 'isActive': 0}
    ]
    return all_packages
