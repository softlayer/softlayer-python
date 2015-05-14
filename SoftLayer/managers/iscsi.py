"""
    SoftLayer.iscsi
    ~~~~~~~~~~~~~~~
    ISCSI Manager/helpers

    :license: MIT, see LICENSE for more details.
"""
from SoftLayer import exceptions
from SoftLayer import utils


class ISCSIManager(utils.IdentifierMixin, object):
    """Manages iSCSI storages."""

    def __init__(self, client):
        self.configuration = {}
        self.client = client
        self.iscsi_svc = self.client['Network_Storage_Iscsi']
        self.product_order = self.client['Product_Order']

    def _find_item_prices(self, size, categorycode=''):
        """Retrieves the Item Price IDs."""
        item_prices = self.client['Product_Package'].getItems(
            id=0,
            mask='id,capacity,prices[id]',
            filter={
                'items': {
                    'capacity': {'operation': int(size)},
                    'categories': {
                        'categoryCode': {'operation': categorycode}
                    }}})

        for item_price in item_prices:
            for price in item_price['prices']:
                return price['id']

        raise exceptions.SoftLayerError(
            "Could not find a valid price with for the given size")

    def _build_order(self, item_price, location):
        """Returns a dict appropriate for Product_Order::placeOrder()."""

        location_id = self._get_location_id(location)
        order = {
            'complexType':
            'SoftLayer_Container_Product_Order_Network_Storage_Iscsi',
            'location': location_id,
            'packageId': 0,  # storage package
            'prices': [{'id': item_price}],
            'quantity': 1
        }
        return order

    def _get_location_id(self, location):
        """Returns location id of datacenter for ProductOrder::placeOrder()."""
        loc_svc = self.client['Location_Datacenter']
        datacenters = loc_svc.getDatacenters(mask='mask[longName,id,name]')
        for datacenter in datacenters:
            if datacenter['name'] == location:
                location = datacenter['id']
                return location
        raise ValueError('Invalid datacenter name specified.')

    def create_iscsi(self, size=None, location=None):
        """Places an order for iSCSI volume.

        :param integer size: size of iSCSI volume to create
        :param string location: datacenter to use to create volume in
        """
        item_price = self._find_item_prices(int(size),
                                            categorycode='iscsi')
        iscsi_order = self._build_order(item_price, location)
        return self.product_order.placeOrder(iscsi_order)

    def list_iscsi(self):
        """List iSCSI volume."""
        account = self.client['Account']
        iscsi_list = account.getIscsiNetworkStorage(
            mask='eventCount,serviceResource[datacenter.name]')
        return iscsi_list

    def get_iscsi(self, volume_id, **kwargs):
        """Get details about a iSCSI storage.

        :param integer volume_id: the volume ID
        :returns: A dictionary containing a large amount of information about
                  the specified storage.
        """

        if 'mask' not in kwargs:
            items = [
                'id',
                'serviceResourceName',
                'createDate',
                'nasType',
                'capacityGb',
                'snapshotCapacityGb',
                'mountableFlag',
                'serviceResourceBackendIpAddress',
                'billingItem',
                'notes',
                'username',
                'password'
            ]
            kwargs['mask'] = "mask[%s]" % ','.join(items)
        return self.iscsi_svc.getObject(id=volume_id, **kwargs)

    def cancel_iscsi(self, volume_id, reason='unNeeded', immediate=False):
        """Cancels the given iSCSI volume.

        :param integer volume_id: the volume ID

        """
        iscsi = self.get_iscsi(
            volume_id,
            mask='mask[id,capacityGb,username,password,billingItem[id]]')
        billingitemid = iscsi['billingItem']['id']
        self.client['Billing_Item'].cancelItem(
            immediate,
            True,
            reason,
            id=billingitemid)

    def create_snapshot(self, volume_id, notes='No longer needed'):
        """Orders a snapshot for given volume.

        :param integer volume_id: the volume ID
        """

        self.iscsi_svc.createSnapshot(notes, id=volume_id)

    def create_snapshot_space(self, volume_id, capacity):
        """Orders a snapshot space for given volume.

        :param integer volume_id: the volume ID
        :param integer capacity: capacity in ~GB
        """
        item_price = self._find_item_prices(
            int(capacity), categorycode='iscsi_snapshot_space')
        result = self.get_iscsi(
            volume_id, mask='mask[id,capacityGb,serviceResource[datacenter]]')
        snapshotspaceorder = {
            'complexType':
            'SoftLayer_Container_Product_Order_\
Network_Storage_Iscsi_SnapshotSpace',
            'location': result['serviceResource']['datacenter']['id'],
            'packageId': 0,
            'prices': [{'id': item_price}],
            'quantity': 1,
            'volumeId': volume_id}
        self.product_order.placeOrder(snapshotspaceorder)

    def delete_snapshot(self, snapshot_id):
        """Deletes the given snapshot.

        :params: integer snapshot_id: the snapshot ID
        """

        self.iscsi_svc.deleteObject(id=snapshot_id)

    def restore_from_snapshot(self, volume_id, snapshot_id):
        """Restore the volume to snapshot's contents.

        :params: imteger volume_id: the volume ID
        :params: integer snapshot_id: the snapshot ID
        """
        self.iscsi_svc.restoreFromSnapshot(snapshot_id, id=volume_id)
