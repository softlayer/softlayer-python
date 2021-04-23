"""
    SoftLayer.tests.managers.ordering_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
from unittest import mock as mock

import SoftLayer
from SoftLayer import exceptions
from SoftLayer import fixtures
from SoftLayer import testing


class OrderingTests(testing.TestCase):

    def set_up(self):
        self.ordering = SoftLayer.OrderingManager(self.client)

    def test_get_package_by_type_returns_no_outlet_packages(self):
        packages = self._get_server_packages()
        filtered_packages = self.ordering.filter_outlet_packages(packages)

        for package_id in [27, 28]:
            self._assert_package_id_not_present(package_id, filtered_packages)

    def _get_server_packages(self):
        return self.ordering.get_packages_of_type(['BARE_METAL_CPU'])

    def _assert_package_id_not_present(self, package_id, packages):
        package_ids = []
        for package in packages:
            package_ids.append(package['id'])

        self.assertNotIn(package_id, package_ids)

    def test_get_active_packages(self):
        packages = self._get_server_packages()
        filtered_packages = self.ordering.get_only_active_packages(packages)

        for package_id in [15]:
            self._assert_package_id_not_present(package_id, filtered_packages)

    def test_get_package_by_type_returns_if_found(self):
        package_type = "BARE_METAL_CORE"
        mask = "mask[id, name]"
        package = self.ordering.get_package_by_type(package_type, mask)
        self.assertIsNotNone(package)

    def test_get_package_by_type_returns_none_if_not_found(self):
        p_mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        p_mock.return_value = []

        package = self.ordering.get_package_by_type("PIZZA_FLAVORED_SERVERS")

        self.assertIsNone(package)

    def test_get_package_id_by_type_returns_valid_id(self):
        p_mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        p_mock.return_value = [
            {'id': 46, 'name': 'Virtual Servers',
             'description': 'Virtual Server Instances',
             'type': {'keyName': 'VIRTUAL_SERVER_INSTANCE'}, 'isActive': 1},
        ]

        package_type = "VIRTUAL_SERVER_INSTANCE"
        package_id = self.ordering.get_package_id_by_type(package_type)

        self.assertEqual(46, package_id)

    def test_get_preset_prices(self):
        result = self.ordering.get_preset_prices(405)

        self.assertEqual(result, fixtures.SoftLayer_Product_Package_Preset.getObject)
        self.assert_called_with('SoftLayer_Product_Package_Preset', 'getObject')

    def test_get_item_prices(self):
        result = self.ordering.get_item_prices(835)

        self.assertEqual(result, fixtures.SoftLayer_Product_Package.getItemPrices)
        self.assert_called_with('SoftLayer_Product_Package', 'getItemPrices')

    def test_get_package_id_by_type_fails_for_nonexistent_package_type(self):
        p_mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        p_mock.return_value = []

        self.assertRaises(ValueError,
                          self.ordering.get_package_id_by_type,
                          "STRAWBERRY_FLAVORED_SERVERS")

    def test_get_order_container(self):
        container = self.ordering.get_order_container(1234)
        self.assertEqual(1, container['quantity'])
        self.assert_called_with('SoftLayer_Billing_Order_Quote', 'getRecalculatedOrderContainer')

    def test_get_quotes(self):
        quotes = self.ordering.get_quotes()
        quotes_fixture = self.ordering.client['Account'].getActiveQuotes()
        self.assertEqual(quotes, quotes_fixture)

    def test_get_quote_details(self):
        quote = self.ordering.get_quote_details(1234)
        quote_service = self.ordering.client['Billing_Order_Quote']
        quote_fixture = quote_service.getObject(id=1234)
        self.assertEqual(quote, quote_fixture)

    def test_save_quote(self):
        saved_quote = self.ordering.save_quote(1234)
        quote_service = self.ordering.client['Billing_Order_Quote']
        quote_fixture = quote_service.getObject(id=1234)
        self.assertEqual(saved_quote, quote_fixture)
        self.assert_called_with('SoftLayer_Billing_Order_Quote', 'saveQuote', identifier=1234)

    def test_verify_quote(self):
        extras = {
            'hardware': [{
                'hostname': 'test1',
                'domain': 'example.com'
            }]
        }
        result = self.ordering.verify_quote(1234, extras)

        self.assertEqual(result, fixtures.SoftLayer_Billing_Order_Quote.verifyOrder)
        self.assert_called_with('SoftLayer_Billing_Order_Quote', 'verifyOrder')

    def test_order_quote_virtual_guest(self):
        guest_quote = {
            'orderContainers': [{
                'presetId': '',
                'prices': [{
                    'id': 1921
                }],
                'quantity': 1,
                'packageId': 46,
                'useHourlyPricing': '',
            }],
        }
        extras = {
            'hardware': [{
                'hostname': 'test1',
                'domain': 'example.com'
            }]
        }
        mock = self.set_mock('SoftLayer_Billing_Order_Quote', 'getRecalculatedOrderContainer')
        mock.return_value = guest_quote
        result = self.ordering.order_quote(1234, extras)

        self.assertEqual(result, fixtures.SoftLayer_Billing_Order_Quote.placeOrder)
        self.assert_called_with('SoftLayer_Billing_Order_Quote', 'placeOrder')

    def test_generate_order_template(self):
        extras = {'hardware': [{'hostname': 'test1', 'domain': 'example.com'}]}

        result = self.ordering.generate_order_template(1234, extras, quantity=1)
        self.assert_called_with('SoftLayer_Billing_Order_Quote', 'getRecalculatedOrderContainer')
        self.assertEqual(result['hardware'][0]['domain'], 'example.com')

    def test_generate_order_template_virtual(self):
        extras = {
            'hardware': [{
                'hostname': 'test1',
                'domain': 'example.com'
            }],
            'testProperty': 100
        }
        result = self.ordering.generate_order_template(1234, extras, quantity=1)
        self.assert_called_with('SoftLayer_Billing_Order_Quote', 'getRecalculatedOrderContainer')
        self.assertEqual(result['testProperty'], 100)

    def test_generate_order_template_extra_quantity(self):
        self.assertRaises(ValueError,
                          self.ordering.generate_order_template,
                          1234, [], quantity=1)

    def test_get_package_by_key_returns_if_found(self):
        package_keyname = "BARE_METAL_SERVER"
        mask = "mask[id, name]"
        package = self.ordering.get_package_by_key(package_keyname, mask)
        self.assertIsNotNone(package)

    def test_get_package_by_key_returns_none_if_not_found(self):
        p_mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        p_mock.return_value = []
        self.assertRaises(exceptions.SoftLayerError, self.ordering.get_package_by_key, 'WILLY_NILLY_SERVERS')

    def test_list_categories(self):
        p_mock = self.set_mock('SoftLayer_Product_Package', 'getConfiguration')
        p_mock.return_value = ['cat1', 'cat2']

        with mock.patch.object(self.ordering, 'get_package_by_key') as mock_get_pkg:
            mock_get_pkg.return_value = {'id': 1234}

            cats = self.ordering.list_categories('PACKAGE_KEYNAME')

        mock_get_pkg.assert_called_once_with('PACKAGE_KEYNAME', mask='id')
        self.assertEqual(p_mock.return_value, cats)

    def test_list_categories_filters(self):
        p_mock = self.set_mock('SoftLayer_Product_Package', 'getConfiguration')
        p_mock.return_value = ['cat1', 'cat2']
        fake_filter = {'test': {'operation': 1234}}
        with mock.patch.object(self.ordering, 'get_package_by_key') as mock_get_pkg:
            mock_get_pkg.return_value = {'id': 1234}

            cats = self.ordering.list_categories('PACKAGE_KEYNAME', filter=fake_filter)

        self.assert_called_with('SoftLayer_Product_Package', 'getConfiguration', filter=fake_filter)
        self.assertEqual(p_mock.return_value, cats)

    def test_list_items(self):
        p_mock = self.set_mock('SoftLayer_Product_Package', 'getItems')
        p_mock.return_value = ['item1', 'item2']

        with mock.patch.object(self.ordering, 'get_package_by_key') as mock_get_pkg:
            mock_get_pkg.return_value = {'id': 1234}

            items = self.ordering.list_items('PACKAGE_KEYNAME')

        mock_get_pkg.assert_called_once_with('PACKAGE_KEYNAME', mask='id')
        self.assertEqual(p_mock.return_value, items)

    def test_list_packages(self):
        packages = [{'id': 1234, 'isActive': True},
                    {'id': 1235, 'isActive': True}]
        p_mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        p_mock.return_value = packages

        actual_pkgs = self.ordering.list_packages()

        self.assertEqual(packages, actual_pkgs)

    def test_list_packages_not_active(self):
        packages = [{'id': 1234, 'isActive': True},
                    {'id': 1235, 'isActive': False}]
        p_mock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        p_mock.return_value = packages

        actual_pkgs = self.ordering.list_packages()

        # Make sure that the list returned only contained the package
        # that was active
        self.assertEqual([packages[0]], actual_pkgs)

    def test_list_presets(self):
        acct_presets = ['acctPreset1', 'acctPreset2']
        active_presets = ['activePreset3', 'activePreset4']

        acct_preset_mock = self.set_mock('SoftLayer_Product_Package', 'getAccountRestrictedActivePresets')
        active_preset_mock = self.set_mock('SoftLayer_Product_Package', 'getActivePresets')
        acct_preset_mock.return_value = acct_presets
        active_preset_mock.return_value = active_presets

        presets = self.ordering.list_presets('PACKAGE_KEYNAME')

        # Make sure the preset list returns both active presets and
        # account restricted presets
        self.assertEqual(active_presets + acct_presets, presets)

    def test_get_preset_by_key(self):
        keyname = 'PRESET_KEYNAME'
        preset_filter = {
            'activePresets': {
                'keyName': {
                    'operation': '_= %s' % keyname
                }
            },
            'accountRestrictedActivePresets': {
                'keyName': {
                    'operation': '_= %s' % keyname
                }
            }
        }

        with mock.patch.object(self.ordering, 'list_presets') as list_mock:
            list_mock.return_value = ['preset1']

            preset = self.ordering.get_preset_by_key('PACKAGE_KEYNAME', keyname)

        list_mock.assert_called_once_with('PACKAGE_KEYNAME', filter=preset_filter, mask=None)
        self.assertEqual(list_mock.return_value[0], preset)

    def test_get_preset_by_key_preset_not_found(self):
        keyname = 'PRESET_KEYNAME'
        preset_filter = {
            'activePresets': {
                'keyName': {
                    'operation': '_= %s' % keyname
                }
            },
            'accountRestrictedActivePresets': {
                'keyName': {
                    'operation': '_= %s' % keyname
                }
            }
        }
        with mock.patch.object(self.ordering, 'list_presets') as list_mock:
            list_mock.return_value = []

            exc = self.assertRaises(exceptions.SoftLayerError,
                                    self.ordering.get_preset_by_key, 'PACKAGE_KEYNAME', keyname)

        list_mock.assert_called_once_with('PACKAGE_KEYNAME', filter=preset_filter, mask=None)
        self.assertEqual('Preset {} does not exist in package {}'.format(keyname, 'PACKAGE_KEYNAME'), str(exc))

    def test_get_price_id_list(self):
        category1 = {'categoryCode': 'cat1'}
        price1 = {'id': 1234, 'locationGroupId': None, 'categories': [{"categoryCode": "guest_core"}],
                  'itemCategory': [category1]}
        item1 = {'id': 1111, 'keyName': 'ITEM1', 'itemCategory': category1, 'prices': [price1]}
        category2 = {'categoryCode': 'cat2'}
        price2 = {'id': 5678, 'locationGroupId': None, 'categories': [category2]}
        item2 = {'id': 2222, 'keyName': 'ITEM2', 'itemCategory': category2, 'prices': [price2]}

        with mock.patch.object(self.ordering, 'list_items') as list_mock:
            list_mock.return_value = [item1, item2]

            prices = self.ordering.get_price_id_list('PACKAGE_KEYNAME', ['ITEM1', 'ITEM2'], "8")

        list_mock.assert_called_once_with('PACKAGE_KEYNAME', mask='id, description, capacity, itemCategory, keyName, '
                                                                  'prices[categories]')
        self.assertEqual([price1['id'], price2['id']], prices)

    def test_get_price_id_list_no_core(self):
        category1 = {'categoryCode': 'cat1'}
        price1 = {'id': 1234, 'locationGroupId': None, 'categories': [{"categoryCode": "guest_core"}],
                  'itemCategory': [category1]}
        item1 = {'id': 1111, 'keyName': 'ITEM1', 'itemCategory': category1, 'prices': [price1]}
        category2 = {'categoryCode': 'cat2'}
        price2 = {'id': 5678, 'locationGroupId': None, 'categories': [category2]}
        item2 = {'id': 2222, 'keyName': 'ITEM2', 'itemCategory': category2, 'prices': [price2]}

        with mock.patch.object(self.ordering, 'list_items') as list_mock:
            list_mock.return_value = [item1, item2]

            prices = self.ordering.get_price_id_list('PACKAGE_KEYNAME', ['ITEM1', 'ITEM2'], None)

        list_mock.assert_called_once_with('PACKAGE_KEYNAME', mask='id, description, capacity, itemCategory, keyName, '
                                                                  'prices[categories]')
        self.assertEqual([price1['id'], price2['id']], prices)

    def test_get_price_id_list_item_not_found(self):
        category1 = {'categoryCode': 'cat1'}
        price1 = {'id': 1234, 'locationGroupId': '', 'categories': [category1]}
        item1 = {'id': 1111, 'keyName': 'ITEM1', 'itemCategory': category1, 'prices': [price1]}

        with mock.patch.object(self.ordering, 'list_items') as list_mock:
            list_mock.return_value = [item1]

            exc = self.assertRaises(exceptions.SoftLayerError,
                                    self.ordering.get_price_id_list,
                                    'PACKAGE_KEYNAME', ['ITEM2'], "8")
        list_mock.assert_called_once_with('PACKAGE_KEYNAME', mask='id, description, capacity, itemCategory, keyName, '
                                                                  'prices[categories]')
        self.assertEqual("Item ITEM2 does not exist for package PACKAGE_KEYNAME", str(exc))

    def test_get_price_id_list_gpu_items_with_two_categories(self):
        # Specific for GPU prices which are differentiated by their category (gpu0, gpu1)
        price1 = {'id': 1234, 'locationGroupId': None, 'categories': [{'categoryCode': 'gpu1'}]}
        price2 = {'id': 5678, 'locationGroupId': None, 'categories': [{'categoryCode': 'gpu0'}]}
        item1 = {'id': 1111, 'keyName': 'ITEM1', 'itemCategory': {'categoryCode': 'gpu0'}, 'prices': [price1, price2]}

        with mock.patch.object(self.ordering, 'list_items') as list_mock:
            list_mock.return_value = [item1, item1]

            prices = self.ordering.get_price_id_list('PACKAGE_KEYNAME', ['ITEM1', 'ITEM1'], "8")

            list_mock.assert_called_once_with('PACKAGE_KEYNAME', mask='id, description, capacity, itemCategory, '
                                                                      'keyName, ' 'prices[categories]')
            self.assertEqual([price2['id'], price1['id']], prices)

    def test_generate_no_complex_type(self):
        pkg = 'PACKAGE_KEYNAME'
        items = ['ITEM1', 'ITEM2']
        exc = self.assertRaises(exceptions.SoftLayerError, self.ordering.generate_order, pkg, 'DALLAS13', items)

        self.assertEqual("A complex type must be specified with the order", str(exc))

    def test_generate_order_with_preset(self):
        pkg = 'PACKAGE_KEYNAME'
        complex_type = 'SoftLayer_Container_Foo'
        items = ['ITEM1', 'ITEM2']
        preset = 'PRESET_KEYNAME'
        expected_order = {'orderContainers': [
            {'complexType': 'SoftLayer_Container_Foo',
             'location': 1854895,
             'packageId': 1234,
             'presetId': 5678,
             'prices': [{'id': 1111}, {'id': 2222}],
             'quantity': 1,
             'useHourlyPricing': True}
        ]}

        mock_pkg, mock_preset, mock_get_ids = self._patch_for_generate()

        order = self.ordering.generate_order(pkg, 'DALLAS13', items, preset_keyname=preset, complex_type=complex_type)

        mock_pkg.assert_called_once_with(pkg, mask='id')
        mock_preset.assert_called_once_with(pkg, preset)
        mock_get_ids.assert_called_once_with(pkg, items, 8)
        self.assertEqual(expected_order, order)

    def test_generate_order_with_quantity(self):
        pkg = 'PACKAGE_KEYNAME'
        quantity = 2
        items = ['ITEM1', 'ITEM2']
        extras = {"hardware": [{"hostname": "test01", "domain": "example.com"},
                               {"hostname": "test02", "domain": "example.com"}]}
        complex_type = 'My_Type'
        expected_order = {'orderContainers': [
            {'complexType': 'My_Type',
             'hardware': [{'domain': 'example.com',
                           'hostname': 'test01'},
                          {'domain': 'example.com',
                           'hostname': 'test02'}],
             'location': 1854895,
             'packageId': 1234,
             'prices': [{'id': 1111}, {'id': 2222}],
             'quantity': 2,
             'useHourlyPricing': True}
        ]}

        mock_pkg, mock_preset, mock_get_ids = self._patch_for_generate()

        order = self.ordering.generate_order(pkg, 'DALLAS13', items, complex_type=complex_type, quantity=quantity,
                                             extras=extras)

        mock_pkg.assert_called_once_with(pkg, mask='id')
        mock_preset.assert_not_called()
        mock_get_ids.assert_called_once_with(pkg, items, None)
        self.assertEqual(expected_order, order)

    def test_generate_order(self):
        pkg = 'PACKAGE_KEYNAME'
        items = ['ITEM1', 'ITEM2']
        complex_type = 'My_Type'
        expected_order = {'orderContainers': [
            {'complexType': 'My_Type',
             'location': 1854895,
             'packageId': 1234,
             'prices': [{'id': 1111}, {'id': 2222}],
             'quantity': 1,
             'useHourlyPricing': True}
        ]}

        mock_pkg, mock_preset, mock_get_ids = self._patch_for_generate()

        order = self.ordering.generate_order(pkg, 'DALLAS13', items, complex_type=complex_type)

        mock_pkg.assert_called_once_with(pkg, mask='id')
        mock_preset.assert_not_called()
        mock_get_ids.assert_called_once_with(pkg, items, None)
        self.assertEqual(expected_order, order)

    def test_verify_order(self):
        ord_mock = self.set_mock('SoftLayer_Product_Order', 'verifyOrder')
        ord_mock.return_value = {'id': 1234}
        pkg = 'PACKAGE_KEYNAME'
        location = 'DALLAS13'
        items = ['ITEM1', 'ITEM2']
        hourly = True
        preset_keyname = 'PRESET'
        complex_type = 'Complex_Type'
        extras = {'foo': 'bar'}
        quantity = 1

        with mock.patch.object(self.ordering, 'generate_order') as gen_mock:
            gen_mock.return_value = {'order': {}}

            order = self.ordering.verify_order(pkg, location, items, hourly=hourly,
                                               preset_keyname=preset_keyname,
                                               complex_type=complex_type,
                                               extras=extras, quantity=quantity)

        gen_mock.assert_called_once_with(pkg, location, items, hourly=hourly,
                                         preset_keyname=preset_keyname,
                                         complex_type=complex_type,
                                         extras=extras, quantity=quantity)
        self.assertEqual(ord_mock.return_value, order)

    def test_place_order(self):
        ord_mock = self.set_mock('SoftLayer_Product_Order', 'placeOrder')
        ord_mock.return_value = {'id': 1234}
        pkg = 'PACKAGE_KEYNAME'
        location = 'DALLAS13'
        items = ['ITEM1', 'ITEM2']
        hourly = True
        preset_keyname = 'PRESET'
        complex_type = 'Complex_Type'
        extras = {'foo': 'bar'}
        quantity = 1

        with mock.patch.object(self.ordering, 'generate_order') as gen_mock:
            gen_mock.return_value = {'order': {}}

            order = self.ordering.place_order(pkg, location, items, hourly=hourly,
                                              preset_keyname=preset_keyname,
                                              complex_type=complex_type,
                                              extras=extras, quantity=quantity)

        gen_mock.assert_called_once_with(pkg, location, items, hourly=hourly,
                                         preset_keyname=preset_keyname,
                                         complex_type=complex_type,
                                         extras=extras, quantity=quantity)
        self.assertEqual(ord_mock.return_value, order)

    def test_place_order_with_quantity(self):
        ord_mock = self.set_mock('SoftLayer_Product_Order', 'placeOrder')
        ord_mock.return_value = {'id': 1234}
        pkg = 'PACKAGE_KEYNAME'
        location = 'DALLAS13'
        items = ['ITEM1', 'ITEM2']
        hourly = True
        preset_keyname = 'PRESET'
        complex_type = 'Complex_Type'
        extras = {"hardware": [{"hostname": "test01", "domain": "example.com"},
                               {"hostname": "test02", "domain": "example.com"}]}
        quantity = 2

        with mock.patch.object(self.ordering, 'generate_order') as gen_mock:
            gen_mock.return_value = {'order': {}}

            order = self.ordering.place_order(pkg, location, items, hourly=hourly,
                                              preset_keyname=preset_keyname,
                                              complex_type=complex_type,
                                              extras=extras, quantity=quantity)

        gen_mock.assert_called_once_with(pkg, location, items, hourly=hourly,
                                         preset_keyname=preset_keyname,
                                         complex_type=complex_type,
                                         extras=extras, quantity=quantity)
        self.assertEqual(ord_mock.return_value, order)

    def test_place_quote(self):
        ord_mock = self.set_mock('SoftLayer_Product_Order', 'placeQuote')
        ord_mock.return_value = {'id': 1234}
        pkg = 'PACKAGE_KEYNAME'
        location = 'DALLAS13'
        items = ['ITEM1', 'ITEM2']
        hourly = False
        preset_keyname = 'PRESET'
        complex_type = 'Complex_Type'
        extras = {'foo': 'bar'}
        quantity = 1
        name = 'wombat'
        send_email = True

        with mock.patch.object(self.ordering, 'generate_order') as gen_mock:
            gen_mock.return_value = {'order': {}}

            order = self.ordering.place_quote(pkg, location, items, preset_keyname=preset_keyname,
                                              complex_type=complex_type, extras=extras, quantity=quantity,
                                              quote_name=name, send_email=send_email)

        gen_mock.assert_called_once_with(pkg, location, items, hourly=hourly,
                                         preset_keyname=preset_keyname,
                                         complex_type=complex_type,
                                         extras=extras, quantity=quantity)
        self.assertEqual(ord_mock.return_value, order)

    def test_locations(self):
        locations = self.ordering.package_locations('BARE_METAL_CPU')
        self.assertEqual('WASHINGTON07', locations[0]['keyname'])

    def _patch_for_generate(self):
        # mock out get_package_by_key, get_preset_by_key, and get_price_id_list
        # with patchers
        mock_pkg = mock.patch.object(self.ordering, 'get_package_by_key')
        mock_preset = mock.patch.object(self.ordering, 'get_preset_by_key')
        mock_get_ids = mock.patch.object(self.ordering, 'get_price_id_list')

        # start each patcher, and set a cleanup to stop each patcher as well
        to_return = []
        for mock_func in [mock_pkg, mock_preset, mock_get_ids]:
            to_return.append(mock_func.start())
            self.addCleanup(mock_func.stop)

        # set the return values on each of the mocks
        to_return[0].return_value = {'id': 1234}
        to_return[1].return_value = {'id': 5678}
        to_return[2].return_value = [1111, 2222]
        return to_return

    def test_get_location_id_short(self):
        locations = self.set_mock('SoftLayer_Location', 'getDatacenters')
        locations.return_value = [{'id': 1854895, 'name': 'dal13', 'regions': [{'keyname': 'DALLAS13'}]}]
        dc_id = self.ordering.get_location_id('dal13')
        self.assertEqual(1854895, dc_id)

    def test_get_location_id_keyname(self):
        locations = self.set_mock('SoftLayer_Location', 'getDatacenters')
        locations.return_value = [{'id': 1854895, 'name': 'dal13', 'regions': [{'keyname': 'DALLAS13'}]}]
        dc_id = self.ordering.get_location_id('DALLAS13')
        self.assertEqual(1854895, dc_id)

    def test_get_location_id_exception(self):
        locations = self.set_mock('SoftLayer_Location', 'getDatacenters')
        locations.return_value = []
        self.assertRaises(exceptions.SoftLayerError, self.ordering.get_location_id, "BURMUDA")

    def test_get_location_id_int(self):
        dc_id = self.ordering.get_location_id(1234)
        self.assertEqual(1234, dc_id)

    def test_get_location_id_NONE(self):
        dc_id = self.ordering.get_location_id("NONE")
        self.assertEqual(0, dc_id)

    def test_location_group_id_none(self):
        # RestTransport uses None for empty locationGroupId
        category1 = {'categoryCode': 'cat1'}
        price1 = {'id': 1234, 'locationGroupId': None, 'categories': [category1]}
        item1 = {'id': 1111, 'keyName': 'ITEM1', 'itemCategory': category1, 'prices': [price1]}
        category2 = {'categoryCode': 'cat2'}
        price2 = {'id': 5678, 'locationGroupId': None, 'categories': [category2]}
        item2 = {'id': 2222, 'keyName': 'ITEM2', 'itemCategory': category2, 'prices': [price2]}

        with mock.patch.object(self.ordering, 'list_items') as list_mock:
            list_mock.return_value = [item1, item2]

            prices = self.ordering.get_price_id_list('PACKAGE_KEYNAME', ['ITEM1', 'ITEM2'], "8")

        list_mock.assert_called_once_with('PACKAGE_KEYNAME', mask='id, description, capacity, itemCategory, keyName, '
                                                                  'prices[categories]')
        self.assertEqual([price1['id'], price2['id']], prices)

    def test_location_groud_id_empty(self):
        # XMLRPCtransport uses '' for empty locationGroupId
        category1 = {'categoryCode': 'cat1'}
        price1 = {'id': 1234, 'locationGroupId': '', 'categories': [category1]}
        item1 = {'id': 1111, 'keyName': 'ITEM1', 'itemCategory': category1, 'prices': [price1]}
        category2 = {'categoryCode': 'cat2'}
        price2 = {'id': 5678, 'locationGroupId': "", 'categories': [category2]}
        item2 = {'id': 2222, 'keyName': 'ITEM2', 'itemCategory': category2, 'prices': [price2]}

        with mock.patch.object(self.ordering, 'list_items') as list_mock:
            list_mock.return_value = [item1, item2]

            prices = self.ordering.get_price_id_list('PACKAGE_KEYNAME', ['ITEM1', 'ITEM2'], "8")

        list_mock.assert_called_once_with('PACKAGE_KEYNAME', mask='id, description, capacity, itemCategory, keyName, '
                                                                  'prices[categories]')
        self.assertEqual([price1['id'], price2['id']], prices)

    def test_get_item_price_id_without_capacity_restriction(self):
        category1 = {'categoryCode': 'cat1'}
        category2 = {'categoryCode': 'cat2'}
        prices = [{'id': 1234, 'locationGroupId': '', 'categories': [category1]},
                  {'id': 2222, 'locationGroupId': 509, 'categories': [category2]}]

        price_id = self.ordering.get_item_price_id("8", prices)

        self.assertEqual(1234, price_id)

    def test_get_item_price_id_core_with_capacity_restriction(self):
        category1 = {'categoryCode': 'cat1'}
        price1 = [{'id': 1234, 'locationGroupId': '', "capacityRestrictionMaximum": "16",
                   "capacityRestrictionMinimum": "1", "capacityRestrictionType": "CORE",
                   'categories': [category1]},
                  {'id': 2222, 'locationGroupId': '', "capacityRestrictionMaximum": "56",
                   "capacityRestrictionMinimum": "36", "capacityRestrictionType": "CORE",
                   'categories': [category1]}]

        price_id = self.ordering.get_item_price_id("8", price1)

        self.assertEqual(1234, price_id)

    def test_get_item_price_id_storage_with_capacity_restriction(self):
        category1 = {'categoryCode': 'cat1'}
        price1 = [{'id': 1234, 'locationGroupId': '', "capacityRestrictionMaximum": "16",
                   "capacityRestrictionMinimum": "1", "capacityRestrictionType": "STORAGE_SPACE",
                   'categories': [category1]},
                  {'id': 2222, 'locationGroupId': '', "capacityRestrictionMaximum": "56",
                   "capacityRestrictionMinimum": "36", "capacityRestrictionType": "STORAGE_SPACE",
                   'categories': [category1]}]

        price_id = self.ordering.get_item_price_id("8", price1)

        self.assertEqual(1234, price_id)

    def test_get_item_price_id_processor_with_capacity_restriction(self):
        category1 = {'categoryCode': 'cat1'}
        price1 = [{'id': 1234, 'locationGroupId': '', "capacityRestrictionMaximum": "1",
                   "capacityRestrictionMinimum": "1", "capacityRestrictionType": "PROCESSOR",
                   'categories': [category1]}]

        price_id = self.ordering.get_item_price_id("8", price1)

        self.assertEqual(1234, price_id)

    def test_issues1067(self):
        # https://github.com/softlayer/softlayer-python/issues/1067
        item_mock = self.set_mock('SoftLayer_Product_Package', 'getItems')
        item_mock_return = [
            {
                'id': 10453,
                'itemCategory': {'categoryCode': 'server'},
                "description": "Dual Intel Xeon Silver 4110 (16 Cores, 2.10 GHz)",
                'keyName': 'INTEL_INTEL_XEON_4110_2_10',
                'prices': [
                    {
                        'capacityRestrictionType': 'PROCESSOR',
                        'categories': [{'categoryCode': 'os'}],
                        'id': 201161,
                        'locationGroupId': None,
                        'recurringFee': '250',
                        'setupFee': '0'
                    }
                ]
            }
        ]
        item_mock.return_value = item_mock_return
        item_keynames = ['INTEL_INTEL_XEON_4110_2_10']
        package = 'DUAL_INTEL_XEON_PROCESSOR_SCALABLE_FAMILY_4_DRIVES'
        result = self.ordering.get_price_id_list(package, item_keynames, None)
        self.assertIn(201161, result)

    def test_clean_quote_verify(self):
        extras = {
            'hardware': [{
                'hostname': 'test1',
                'domain': 'example.com'
            }],
            'testPropertyEmpty': '',
            'testPropertyNone': None
        }
        result = self.ordering.verify_quote(1234, extras)

        self.assertEqual(result, fixtures.SoftLayer_Billing_Order_Quote.verifyOrder)
        self.assert_called_with('SoftLayer_Billing_Order_Quote', 'verifyOrder')
        call = self.calls('SoftLayer_Billing_Order_Quote', 'verifyOrder')[0]
        order_container = call.args[0]
        self.assertNotIn('testPropertyEmpty', order_container)
        self.assertNotIn('testPropertyNone', order_container)
        self.assertNotIn('reservedCapacityId', order_container)

    def test_get_item_capacity_core(self):

        items = [{
            "capacity": "1",
            "id": 6131,
            "keyName": "OS_RHEL_7_X_LAMP_64_BIT",
        },
            {
                "capacity": "1",
                "id": 10201,
                "keyName": "GUEST_CORE_1_DEDICATED",
        }]

        item_capacity = self.ordering.get_item_capacity(items, ['GUEST_CORE_1_DEDICATED', 'OS_RHEL_7_X_LAMP_64_BIT'])

        self.assertEqual(1, int(item_capacity))

    def test_get_item_capacity_storage(self):

        items = [{
            "capacity": "1",
            "id": 6131,
            "keyName": "STORAGE_SPACE_FOR_2_IOPS_PER_GB",
        },
            {
                "capacity": "1",
                "id": 10201,
                "keyName": "READHEAVY_TIER",
        }]

        item_capacity = self.ordering.get_item_capacity(items, ['READHEAVY_TIER', 'STORAGE_SPACE_FOR_2_IOPS_PER_GB'])

        self.assertEqual(1, int(item_capacity))

    def test_get_item_capacity_intel(self):

        items = [{
            "capacity": "1",
            "id": 6131,
            "description": "Dual Intel Xeon E5-2690 v3 (24 Cores, 2.60 GHz)",
            "keyName": "INTEL_XEON_2690_2_60",
        },
            {
                "capacity": "1",
                "id": 10201,
                "keyName": "GUEST_CORE_1_DEDICATED",
        }]

        item_capacity = self.ordering.get_item_capacity(items, ['INTEL_XEON_2690_2_60', 'BANDWIDTH_20000_GB'])

        self.assertEqual(24, int(item_capacity))

    def test_get_oder_detail_mask(self):
        order_id = 12345
        test_mask = 'mask[id]'
        self.ordering.get_order_detail(order_id, mask=test_mask)
        self.assert_called_with('SoftLayer_Billing_Order', 'getObject', identifier=order_id, mask=test_mask)

    def test_get_oder_detail_default_mask(self):
        order_id = 12345
        _default_mask = (
            'mask[orderTotalAmount,orderApprovalDate,'
            'initialInvoice[id,amount,invoiceTotalAmount,'
            'invoiceTopLevelItems[id, description, hostName, domainName, oneTimeAfterTaxAmount,'
            'recurringAfterTaxAmount, createDate,'
            'categoryCode,'
            'category[name],'
            'location[name],'
            'children[id, category[name], description, oneTimeAfterTaxAmount,recurringAfterTaxAmount]]],'
            'items[description],userRecord[displayName,userStatus]]')
        self.ordering.get_order_detail(order_id)
        self.assert_called_with('SoftLayer_Billing_Order', 'getObject', identifier=order_id, mask=_default_mask)

    def test_get_item_prices_by_location_name(self):
        object_mask = "filteredMask[pricingLocationGroup[locations]]"
        object_filter = {
            "itemPrices": {"pricingLocationGroup": {"locations": {"name": {"operation": 'dal13'}}}}}
        self.ordering.get_item_prices_by_location('dal13', 'TEST')

        self.assert_called_with('SoftLayer_Product_Package', 'getItemPrices', mask=object_mask, filter=object_filter)

    def test_get_item_prices_by_location_keyname(self):
        object_mask = "filteredMask[pricingLocationGroup[locations]]"
        object_filter = {
            "itemPrices": {"pricingLocationGroup": {"locations": {"name": {"operation": 'dal13'}}}}}
        self.ordering.get_item_prices_by_location('DALLAS13', 'TEST')

        self.assert_called_with('SoftLayer_Product_Package', 'getItemPrices', mask=object_mask, filter=object_filter)

    def test_resolve_location_name(self):
        location_name_expected = 'dal13'
        object_mask = "mask[regions]"
        location_name = self.ordering.resolve_location_name('DALLAS13')
        self.assertEqual(location_name, location_name_expected)
        self.assert_called_with('SoftLayer_Location', 'getDatacenters', mask=object_mask)

    def test_resolve_location_name_by_keyname(self):
        location_name_expected = 'dal13'
        object_mask = "mask[regions]"
        location_name = self.ordering.resolve_location_name('DALLAS13')
        self.assertEqual(location_name, location_name_expected)
        self.assert_called_with('SoftLayer_Location', 'getDatacenters', mask=object_mask)

    def test_resolve_location_name_by_name(self):
        location_name_expected = 'dal13'
        object_mask = "mask[regions]"
        location_name = self.ordering.resolve_location_name('dal13')
        self.assertEqual(location_name, location_name_expected)
        self.assert_called_with('SoftLayer_Location', 'getDatacenters', mask=object_mask)

    def test_resolve_location_name_invalid(self):
        exc = self.assertRaises(exceptions.SoftLayerError, self.ordering.resolve_location_name, None)
        self.assertIn("Invalid location", str(exc))

    def test_resolve_location_name_not_exist(self):
        exc = self.assertRaises(exceptions.SoftLayerError,
                                self.ordering.resolve_location_name, "UNKNOWN_LOCATION_TEST")
        self.assertIn("does not exist", str(exc))

    # https://github.com/softlayer/softlayer-python/issues/1425
    # Issues relating to checking prices based of the price.term relationship
    def test_issues1425_zeroterm(self):
        category1 = {'categoryCode': 'cat1'}
        price1 = {'id': 1234, 'locationGroupId': '', "capacityRestrictionMaximum": "16",
                  "capacityRestrictionMinimum": "1", "capacityRestrictionType": "STORAGE_SPACE",
                  'categories': [category1], 'termLength': 36}
        price2 = {'id': 45678, 'locationGroupId': '', "capacityRestrictionMaximum": "16",
                  "capacityRestrictionMinimum": "1", "capacityRestrictionType": "STORAGE_SPACE",
                  'categories': [category1], 'termLength': 0}

        # Test 0 termLength
        price_id = self.ordering.get_item_price_id("8", [price2, price1])
        self.assertEqual(45678, price_id)

        # Test None termLength
        price2['termLength'] = None
        price_id = self.ordering.get_item_price_id("8", [price2, price1])
        self.assertEqual(45678, price_id)

        # Test '' termLength
        price2['termLength'] = ''
        price_id = self.ordering.get_item_price_id("8", [price2, price1])
        self.assertEqual(45678, price_id)

    def test_issues1425_nonzeroterm(self):
        category1 = {'categoryCode': 'cat1'}
        price1 = {'id': 1234, 'locationGroupId': '', "capacityRestrictionMaximum": "16",
                  "capacityRestrictionMinimum": "1", "capacityRestrictionType": "STORAGE_SPACE",
                  'categories': [category1], 'termLength': 36}
        price2 = {'id': 45678, 'locationGroupId': '', "capacityRestrictionMaximum": "16",
                  "capacityRestrictionMinimum": "1", "capacityRestrictionType": "STORAGE_SPACE",
                  'categories': [category1], 'termLength': 0}

        # Test 36 termLength
        price_id = self.ordering.get_item_price_id("8", [price2, price1], 36)
        self.assertEqual(1234, price_id)

        # Test None-existing price for term
        price_id = self.ordering.get_item_price_id("8", [price2, price1], 37)
        self.assertEqual(None, price_id)
