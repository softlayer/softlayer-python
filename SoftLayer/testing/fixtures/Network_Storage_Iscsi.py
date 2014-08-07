getObject = {
    'accountId': 1111,
    'billingItem': {'id': 600},
    'capacityGb': 20,
    'createDate': '2014:50:15-04:00',
    'guestId': '',
    'hardwareId': '',
    'hostId': '',
    'id': 100,
    'nasType': 'ISCSI',
    'notes': """{'status': 'available'}""",
    'password': 'abcdef',
    'serviceProviderId': 1,
    'serviceResource': {'datacenter': {'id': 138124}},
    'serviceResourceBackendIpAddress': '10.0.1.1',
    'serviceResourceName': 'storagesng0101',
    'username': 'username'
}

createSnapshot = {
    'accountId': 1111,
    'capacityGb': 20,
    'createDate': '2014:51:11-04:00',
    'guestId': '',
    'hardwareId': '',
    'hostId': '',
    'id': 101,
    'nasType': 'ISCSI_SNAPSHOT',
    'parentVolume': {
        'accountId': 1111,
        'capacityGb': 20,
        'createDate': '2014:38:47-04:00',
        'guestId': '',
        'hardwareId': '',
        'hostId': '',
        'id': 100,
        'nasType': 'ISCSI',
        'password': 'abcdef',
        'properties': [
            {'createDate': '2014:40:22-04:00',
             'modifyDate': '',
             'type': {
                 'description':
                 'Percent of reserved snapshot space that is available',
                 'keyname': 'SNAPSHOT_RESERVE_AVAILABLE',
                 'name': 'Snaphot Reserve Available'},

             'value': '100',
             'volumeId': 2233}],

        'propertyCount': 0,
        'serviceProviderId': 1,
        'name': 'storagedal05',
        'snapshotCapacityGb': '40',
        'username': 'username'},
    'password': 'abcdef',
    'serviceProviderId': 1,
    'serviceResource': {'backendIpAddress': '10.1.0.1',
                        'name': 'storagedal05',
                        'type': {'type': 'ISCSI'}},
    'serviceResourceBackendIpAddress': '10.1.0.1',
    'serviceResourceName': 'storagedal05',
    'username': 'username'}

restoreFromSnapshot = True
editObject = True
createObject = getObject
deleteObject = True
