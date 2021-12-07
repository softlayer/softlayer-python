"""
    SoftLayer.tests.managers.storage_generic_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""

import SoftLayer
from SoftLayer import testing


class StorageGenericTests(testing.TestCase):
    def set_up(self):
        self.storage = SoftLayer.managers.storage.StorageManager(self.client)

    def test_get_volume_snapshot_notification_status(self):
        mock = self.set_mock('SoftLayer_Network_Storage', 'getSnapshotNotificationStatus')
        # These are the values we expect from the API as of 2021-12-01, FBLOCK4193
        mock.side_effect = [None, '1', '0']
        expected = [1, 1, 0]

        for expect in expected:
            result = self.storage.get_volume_snapshot_notification_status(12345)
            self.assert_called_with('SoftLayer_Network_Storage', 'getSnapshotNotificationStatus', identifier=12345)
            self.assertEqual(expect, result)

    def test_set_volume_snapshot_notification(self):
        mock = self.set_mock('SoftLayer_Network_Storage', 'setSnapshotNotification')
        mock.return_value = None

        result = self.storage.set_volume_snapshot_notification(12345, False)
        self.assert_called_with('SoftLayer_Network_Storage', 'setSnapshotNotification',
                                identifier=12345, args=(False,))
        self.assertEqual(None, result)
