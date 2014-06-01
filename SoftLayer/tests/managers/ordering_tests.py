"""
    SoftLayer.tests.managers.ordering_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
from SoftLayer import OrderingManager
from SoftLayer.tests import unittest, FixtureClient


class OrderingTests(unittest.TestCase):

    def setUp(self):
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
