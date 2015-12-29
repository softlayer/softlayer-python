"""
    SoftLayer.tests.managers.block_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""

import SoftLayer
from SoftLayer import fixtures
from SoftLayer import testing


class BlockTests(testing.TestCase):
    def set_up(self):
        self.block = SoftLayer.BlockStorageManager(self.client)

    def test_get_block_volume_details(self):
        result = self.block.get_block_volume_details(100)

        self.assertEqual(fixtures.SoftLayer_Network_Storage.getObject,
                         result)
        self.assert_called_with('SoftLayer_Network_Storage', 'getObject',
                                identifier=100)

    def test_list_block_volumes(self):
        result = self.block.list_block_volumes()

        self.assertEqual(fixtures.SoftLayer_Account.getIscsiNetworkStorage,
                         result)
        self.assert_called_with('SoftLayer_Account', 'getIscsiNetworkStorage')

    def test_get_block_volume_access_list(self):
        result = self.block.get_block_volume_access_list(100)

        self.assertEqual(fixtures.SoftLayer_Network_Storage.getObject,
                         result)
        self.assert_called_with('SoftLayer_Network_Storage', 'getObject',
                                identifier=100)

    def test_get_block_volume_snapshot_list(self):
        result = self.block.get_block_volume_access_list(100)

        self.assertEqual(fixtures.SoftLayer_Network_Storage.getObject,
                         result)
        self.assert_called_with('SoftLayer_Network_Storage', 'getObject',
                                identifier=100)

    def test_delete_snapshot(self):
        result = self.block.delete_snapshot(100)

        self.assertEqual(fixtures.SoftLayer_Network_Storage.deleteObject,
                         result)
        self.assert_called_with('SoftLayer_Network_Storage', 'deleteObject',
                                identifier=100)
