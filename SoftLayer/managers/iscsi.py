"""
    SoftLayer.iscsi
    ~~~~~~~~~~~~~~~
    ISCSI Manager/helpers
"""
from SoftLayer.utils import NestedDict, query_filter, IdentifierMixin


class ISCSIManager(IdentifierMixin, object):

    """ Manages iSCSI storages """

    def __init__(self, client):
        self.configuration = {}
        self.client = client
        self.iscsi_svc = self.client['Network_Storage_Iscsi']
        self.product_order = self.client['Product_Order']

    def _find_item_prices(self, size, query='', zero_recurring=False):
        """ Retrieves the Item Price IDs
        """

        item_prices = []
        _filter = NestedDict({})
        _filter[
            'itemPrices'][
            'item'][
            'description'] = query_filter(
            query)
        _filter['itemPrices']['item']['capacity'] = query_filter('%s' % size)

        if not zero_recurring:
            _filter['itemPrices']['recurringFee'] = query_filter('>1')

        iscsi_item_prices = self.client['Product_Package'].getItemPrices(
            id=0,
            filter=_filter.to_dict())
        iscsi_item_prices = sorted(
            iscsi_item_prices,
            key=lambda x:
            (float(x['item']['capacity']),
                float(x.get('recurringFee', 0))))
        for price in iscsi_item_prices:
            item_prices.append(price['id'])
        return item_prices

    def _build_order(self, item_price, location):
        """ Returns a dict appropriate to pass into Product_Order::placeOrder()
        """

        location_id = self._get_location_id(location)
        order = {
            'complexType':
            'SoftLayer_Container_Product_Order_Network_Storage_Iscsi',
            'location': location_id,
            'packageId': 0,  # storage package
            'prices': [{'id': item_price[0]}],
            'quantity': 1
        }
        return order

    def _get_location_id(self, location):
        """ Returns location id of datacenter to pass into
            ProductOrder::placeOrder()
        """
        loc_svc = self.client['Location_Datacenter']
        datacenters = loc_svc.getDatacenters(mask='mask[longName,id,name]')
        for datacenter in datacenters:
            if datacenter['name'] == location[0]:
                location = datacenter['id']
                return location
        raise ValueError('Invalid datacenter name specified.')

    def create_iscsi(self, size=None, location=None, zero_recurring=False):
        """Places an order for iSCSI volume
        :param integer size: size of iSCSI volume to create
        :param string location: datacenter to use to create volume in
        :param boolean zero_recurring: Prefer <$1 recurring fee.
            Even if API shows <$1 volumes, many users are not
            allowed order them. Those who are allowed to order
            the <$1 volumes, can use this flag.
        """
        item_price = self._find_item_prices(size,
                                            zero_recurring=zero_recurring,
                                            query='~GB iSCSI SAN Storage')
        iscsi_order = self._build_order(item_price, location)
        self.product_order.verifyOrder(iscsi_order)
        self.product_order.placeOrder(iscsi_order)

    def get_iscsi(self, volume_id, **kwargs):
        """ Get details about a iSCSI storage

        :param integer volume_id: the volume ID
        :returns: A dictionary containing a large amount of information about
                  the specified storage.

        """

        if 'mask' not in kwargs:
            items = set([
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
            ])
            kwargs['mask'] = "mask[%s]" % ','.join(items)
        return self.iscsi_svc.getObject(id=volume_id, **kwargs)

    def cancel_iscsi(self, volume_id, reason='unNeeded', immediate=False):
        """ Cancels the given iSCSI volume

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
        """ Orders a snapshot for given volume

        :param integer volume_id: the volume ID
        """

        self.iscsi_svc.createSnapshot(notes, id=volume_id)

    def create_snapshot_space(self, volume_id, capacity):
        """ Orders a snapshot space for given volume

        :param integer volume_id: the volume ID
        :param integer capacity: capacity in ~GB
        """
        item_price = self._find_item_prices(
            int(capacity), query='~iSCSI SAN Snapshot Space')
        result = self.get_iscsi(
            volume_id, mask='mask[id,capacityGb,serviceResource[datacenter]]')
        snapshotspaceorder = {
            'complexType':
            'SoftLayer_Container_Product_Order_\
Network_Storage_Iscsi_SnapshotSpace',
            'location': result['serviceResource']['datacenter']['id'],
            'packageId': 0,
            'prices': [{'id': item_price[0]}],
            'quantity': 1,
            'volumeId': volume_id}
        self.product_order.verifyOrder(snapshotspaceorder)
        self.product_order.placeOrder(snapshotspaceorder)

    def delete_snapshot(self, snapshot_id):
        """ Deletes the given snapshot

        :params: integer snapshot_id: the snapshot ID
        """

        self.iscsi_svc.deleteObject(id=snapshot_id)

    def restore_from_snapshot(self, volume_id, snapshot_id):
        """ Restore the volume to snapshot's contents
        :params: imteger volume_id: the volume ID
        :params: integer snapshot_id: the snapshot ID
        """
        self.iscsi_svc.restoreFromSnapshot(snapshot_id, id=volume_id)
