"""
    SoftLayer.tests.managers.ordering_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
from SoftLayer import OrderingManager
from SoftLayer.tests import TestCase, FixtureClient


class OrderingTests(TestCase):

    def set_up(self):
        self.client = FixtureClient()
        self.ordering = OrderingManager(self.client)

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
