"""
    SoftLayer.tests.managers.ordering_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import SoftLayer
from SoftLayer import testing


class OrderingTests(testing.TestCase):

    def set_up(self):
        self.client = testing.FixtureClient()
        self.ordering = SoftLayer.OrderingManager(self.client)

    def test_get_package_by_type_returns_no_outlet_packages(self):
        fixture_outlet_package_ids = [27, 28]
        packages = self._get_server_packages()
        filtered_packages = self.ordering.filter_outlet_packages(packages)

        for package_id in fixture_outlet_package_ids:
            self._assert_package_id_not_present(package_id, filtered_packages)

    def _get_server_packages(self):
        mask = 'id, name, description, type, isActive'
        return self.ordering.get_packages_of_type(['BARE_METAL_CPU'], mask)

    def _assert_package_id_not_present(self, package_id, packages):
        package_ids = []
        for package in packages:
            package_ids.append(package['id'])

        self.assertNotIn(package_id, package_ids)

    def test_get_active_packages(self):
        fixture_inactive_package_ids = [15]
        packages = self._get_server_packages()
        filtered_packages = self.ordering.get_only_active_packages(packages)

        for package_id in fixture_inactive_package_ids:
            self._assert_package_id_not_present(package_id, filtered_packages)

    def test_get_package_by_type_returns_if_found(self):
        package_type = "BARE_METAL_CORE"
        mask = "mask[id, name]"
        package = self.ordering.get_package_by_type(package_type, mask)
        self.assertIsNotNone(package)

    def test_get_package_by_type_returns_none_if_not_found(self):
        package_type = "PIZZA_FLAVORED_SERVERS"
        mask = "mask[id, name]"
        self.ordering.client['Product_Package'].getAllObjects.return_value = []
        package = self.ordering.get_package_by_type(package_type, mask)
        self.assertIsNone(package)

    def test_get_package_id_by_type_returns_valid_id(self):
        package_type = "VIRTUAL_SERVER_INSTANCE"
        self.ordering.client['Product_Package'].getAllObjects.return_value = [
            {'id': 46, 'name': 'Virtual Servers',
             'description': 'Virtual Server Instances',
             'type': {'keyName': 'VIRTUAL_SERVER_INSTANCE'}, 'isActive': 1},
        ]
        package_id = self.ordering.get_package_id_by_type(package_type)
        self.assertEqual(46, package_id)

    def test_get_package_id_by_type_fails_for_nonexistent_package_type(self):
        package_type = "STRAWBERRY_FLAVORED_SERVERS"
        self.ordering.client['Product_Package'].getAllObjects.return_value = []
        with self.assertRaises(ValueError):
            self.ordering.get_package_id_by_type(package_type)

    def test_get_order_container(self):
        container = self.ordering.get_order_container(1234)
        quote = self.ordering.client['Billing_Order_Quote']
        container_fixture = quote.getRecalculatedOrderContainer(id=1234)
        self.assertEqual(container, container_fixture['orderContainers'][0])

    def test_get_quotes(self):
        quotes = self.ordering.get_quotes()
        quotes_fixture = self.ordering.client['Account'].getActiveQuotes()
        self.assertEqual(quotes, quotes_fixture)

    def test_get_quote_details(self):
        quote = self.ordering.get_quote_details(1234)
        quote_service = self.ordering.client['Billing_Order_Quote']
        quote_fixture = quote_service.getObject(id=1234)
        self.assertEqual(quote, quote_fixture)

    def test_verify_quote(self):
        order_service = self.ordering.client['Product_Order']
        result = self.ordering.verify_quote(1234,
                                            [{'hostname': 'test1',
                                              'domain': 'example.com'}],
                                            quantity=1)

        self.assertEqual(result, order_service.verifyOrder())
        self.assertTrue(order_service.verifyOrder.called)

    def test_order_quote(self):
        order_service = self.ordering.client['Product_Order']
        result = self.ordering.verify_quote(1234,
                                            [{'hostname': 'test1',
                                              'domain': 'example.com'}],
                                            quantity=1)

        self.assertEqual(result, order_service.placeOrder())
        self.assertTrue(order_service.placeOrder.called)

    def test_generate_order_template(self):
        result = self.ordering.generate_order_template(
            1234, [{'hostname': 'test1', 'domain': 'example.com'}], quantity=1)
        self.assertEqual(result, {'presetId': None,
                                  'hardware': [{'domain': 'example.com',
                                                'hostname': 'test1'}],
                                  'useHourlyPricing': '',
                                  'packageId': 50,
                                  'prices': [{'id': 1921}],
                                  'quantity': 1})

    def test_generate_order_template_extra_quantity(self):
        with self.assertRaises(ValueError):
            self.ordering.generate_order_template(1234, [], quantity=1)
