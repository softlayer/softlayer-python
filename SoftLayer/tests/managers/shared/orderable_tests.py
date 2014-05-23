"""
    SoftLayer.tests.managers.shared.orderable_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
from SoftLayer.managers.shared.orderable import Orderable
from SoftLayer.tests import unittest, FixtureClient


class CCITests(unittest.TestCase):

    def setUp(self):
        self.client = FixtureClient()
        self.orderable = Orderable()
        self._orig_get_package_service = self.orderable._get_package_service
        self.orderable._get_package_service = self.get_package_service_mock

    def get_package_service_mock(self):
        return self.client['Product_Package']

    def test_orderable_base_class_get_client_raises_exception(self):
        self.orderable._get_package_service = self._orig_get_package_service
        with self.assertRaises(NotImplementedError):
            self.orderable.get_package_id_for_package_type('WHATEVER')

    def test_get_package_id_by_type_returns_matching_packages(self):
        package_type = 'VIRTUAL_SERVER_INSTANCE'
        package_id = self.orderable.get_package_id_for_package_type(
            package_type)
        self.assertEqual(46, package_id)

    def test_get_package_id_by_type_returns_none_when_no_match(self):
        package_type = 'YOLO'
        package_id = self.orderable.get_package_id_for_package_type(
            package_type)
        self.assertIsNone(package_id)