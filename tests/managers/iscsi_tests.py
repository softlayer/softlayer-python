"""
    SoftLayer.tests.managers.iscsi_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""

import SoftLayer
from SoftLayer import fixtures
from SoftLayer import testing


class ISCSITests(testing.TestCase):
    def set_up(self):
        self.iscsi = SoftLayer.ISCSIManager(self.client)

    def test_get_iscsi(self):
        result = self.iscsi.get_iscsi(100)

        self.assertEqual(fixtures.SoftLayer_Network_Storage_Iscsi.getObject,
                         result)
        self.assert_called_with('SoftLayer_Network_Storage_Iscsi', 'getObject',
                                identifier=100)

    def test_cancel_iscsi_immediately(self):
        self.iscsi.cancel_iscsi(600, immediate=True)

        self.assert_called_with('SoftLayer_Billing_Item', 'cancelItem',
                                args=(True, True, 'unNeeded'),
                                identifier=600)

    def test_cancel_iscsi_without_reason(self):
        self.iscsi.cancel_iscsi(600)

        self.assert_called_with('SoftLayer_Billing_Item', 'cancelItem',
                                args=(False, True, 'unNeeded'),
                                identifier=600)

    def test_cancel_iscsi_with_reason(self):
        self.iscsi.cancel_iscsi(600, 'Network Performance')

        self.assert_called_with('SoftLayer_Billing_Item', 'cancelItem',
                                args=(False, True, 'Network Performance'),
                                identifier=600)

    def test_invalid_datacenter(self):
        self.assertRaises(ValueError,
                          self.iscsi.create_iscsi,
                          size=10, location='foo')

    def test_create_iscsi(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getItems')
        mock.return_value = [
            {
                'id': 4439,
                'capacity': '1',
                'description': '1 GB iSCSI Storage',
                'itemCategory': {'categoryCode': 'iscsi'},
                'prices': [{'id': 2222}]
            }
        ]

        self.iscsi.create_iscsi(size=1, location='dal05')

        args = ({'prices': [{'id': 2222}],
                 'quantity': 1,
                 'location': 0,
                 'packageId': 0,
                 'complexType':
                 'SoftLayer_Container_Product_Order_Network_Storage_Iscsi'},)
        self.assert_called_with('SoftLayer_Product_Order', 'placeOrder',
                                args=args)

    def test_delete_snapshot(self):
        self.iscsi.delete_snapshot(1)

        self.assert_called_with('SoftLayer_Network_Storage_Iscsi',
                                'deleteObject',
                                identifier=1)

    def test_create_snapshot(self):
        self.iscsi.create_snapshot(100, 'unNeeded')

        self.assert_called_with('SoftLayer_Network_Storage_Iscsi',
                                'createSnapshot',
                                identifier=100)

    def test_create_snapshot_space(self):
        mock = self.set_mock('SoftLayer_Product_Package', 'getItems')
        mock.return_value = [
            {
                'id': 1121,
                'capacity': '20',
                'description': '20 GB iSCSI snapshot',
                'itemCategory': {'categoryCode': 'iscsi_snapshot_space'},
                'prices': [{'id': 2014}]
            }]

        self.iscsi.create_snapshot_space(100, 20)

        args = (
            {
                'volumeId': 100,
                'location': 138124,
                'packageId': 0,
                'complexType':
                'SoftLayer_Container_'
                'Product_Order_Network_Storage_Iscsi_SnapshotSpace',
                'prices': [{'id': 2014}],
                'quantity': 1,
            },
        )
        self.assert_called_with('SoftLayer_Product_Order', 'placeOrder',
                                args=args)

    def test_restore_from_snapshot(self):
        self.iscsi.restore_from_snapshot(100, 101)

        self.assert_called_with('SoftLayer_Network_Storage_Iscsi',
                                'restoreFromSnapshot',
                                args=(101,),
                                identifier=100)
