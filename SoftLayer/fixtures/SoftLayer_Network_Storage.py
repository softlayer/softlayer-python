getObject = {
    'accountId': 1234,
    'billingItem': {
        'id': 449,
        'cancellationDate': '',
        'categoryCode': 'storage_service_enterprise',
        'activeChildren': [{
            'categoryCode': 'storage_snapshot_space',
            'id': 123,
            'cancellationDate': '',
        }]
    },
    'capacityGb': 20,
    'createDate': '2015:50:15-04:00',
    'guestId': '',
    'hardwareId': '',
    'hostId': '',
    'id': 100,
    'nasType': 'ISCSI',
    'notes': """{'status': 'available'}""",
    'password': '',
    'serviceProviderId': 1,
    'iops': 1000,
    'storageTierLevel': {'description': '2 IOPS per GB'},
    'snapshotCapacityGb': '10',
    'parentVolume': {'snapshotSizeBytes': 1024},
    'osType': {'keyName': 'LINUX'},
    'schedules': [{
        'id': 978,
        'type': {'keyname': 'SNAPSHOT_WEEKLY'},
    }],
    'serviceResource': {'datacenter': {'id': 449500, 'name': 'dal05'}},
    'serviceResourceBackendIpAddress': '10.1.2.3',
    'fileNetworkMountAddress': '127.0.0.1:/TEST',
    'serviceResourceName': 'Storage Type 01 Aggregate staaspar0101_pc01',
    'username': 'username',
    'storageType': {'keyName': 'ENDURANCE_STORAGE'},
    'bytesUsed': 0,
    'activeTransactions': None,
    'activeTransactionCount': 0,
    'allowedVirtualGuests': [{
        'id': 1234,
        'hostname': 'test-server',
        'domain': 'example.com',
        'primaryBackendIpAddress': '10.0.0.1',
        'allowedHost': {
            'name': 'test-server',
            'credential': {'username': 'joe', 'password': '12345'},
        },
    }],
    'lunId': 2,
    'allowedHardware': [{
        'id': 1234,
        'hostname': 'test-server',
        'domain': 'example.com',
        'primaryBackendIpAddress': '10.0.0.2',
        'allowedHost': {
            'name': 'test-server',
            'credential': {'username': 'joe', 'password': '12345'},
        },
    }],
    'allowedSubnets': [{
        'id': 1234,
        'networkIdentifier': '10.0.0.1',
        'cidr': '24',
        'note': 'backend subnet',
        'allowedHost': {
            'name': 'test-server',
            'credential': {'username': 'joe', 'password': '12345'},
        },
    }],
    'allowedIpAddresses': [{
        'id': 1234,
        'ipAddress': '10.0.0.1',
        'note': 'backend ip',
        'allowedHost': {
            'name': 'test-server',
            'credential': {'username': 'joe', 'password': '12345'},
        },
    }],
    'replicationStatus': 'Replicant Volume Provisioning has completed.',
    'replicationPartnerCount': 1,
    'replicationPartners': [{
        'id': 1784,
        'username': 'TEST_REP_1',
        'serviceResourceBackendIpAddress': '10.3.174.79',
        'serviceResource': {'datacenter': {'name': 'wdc01'}},
        'replicationSchedule': {'type': {'keyname': 'REPLICATION_HOURLY'}},
    }, {
        'id': 1785,
        'username': 'TEST_REP_2',
        'serviceResourceBackendIpAddress': '10.3.177.84',
        'serviceResource': {'datacenter': {'name': 'dal01'}},
        'replicationSchedule': {'type': {'keyname': 'REPLICATION_DAILY'}},
    }],
}

getSnapshots = [{
    'id': 470,
    'notes': 'unit_testing_note',
    'snapshotCreationTimestamp': '2016-07-06T07:41:19-05:00',
    'snapshotSizeBytes': '42',
}]

deleteObject = True
allowAccessFromHostList = True
removeAccessFromHostList = True
failoverToReplicant = True
failbackFromReplicant = True
restoreFromSnapshot = True

createSnapshot = {
    'id': 449
}

enableSnapshots = True
disableSnapshots = True
