DUPLICATABLE_VOLUME = {
    'accountId': 1234,
    'activeTransactions': None,
    'activeTransactionCount': 0,
    'billingItem': {
        'activeChildren': [{
            'categoryCode': 'storage_snapshot_space',
            'id': 125,
            'cancellationDate': '',
        }],
        'cancellationDate': '',
        'id': 454,
        'location': {'id': 449500}
    },
    'capacityGb': 500,
    'id': 102,
    'iops': 1000,
    'lunId': 2,
    'osType': {'keyName': 'LINUX'},
    'originalVolumeSize': '500',
    'parentVolume': {'snapshotSizeBytes': 1024},
    'provisionedIops': '1000',
    'replicationPartnerCount': 0,
    'serviceResource': {'datacenter': {'id': 449500, 'name': 'dal05'}},
    'serviceResourceBackendIpAddress': '10.1.2.3',
    'snapshotCapacityGb': '10',
    'storageTierLevel': 'READHEAVY_TIER',
    'storageType': {'keyName': 'ENDURANCE_BLOCK_STORAGE'},
    'username': 'duplicatable_volume_username'
}

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
        }],
        'location': {'id': 449500}
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
    'storageTierLevel': 'READHEAVY_TIER',
    'snapshotCapacityGb': '10',
    'parentVolume': {'snapshotSizeBytes': 1024},
    'osType': {'keyName': 'LINUX'},
    'originalSnapshotName': 'test-origin-snapshot-name',
    'originalVolumeName': 'test-origin-volume-name',
    'originalVolumeSize': '20',
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
        'nasType': 'ISCSI_REPLICANT',
        'createDate': '2017:50:15-04:00',
        'serviceResource': {'datacenter': {'name': 'wdc01'}},
        'replicationSchedule': {'type': {'keyname': 'REPLICATION_HOURLY'}},
    }, {
        'id': 1785,
        'username': 'TEST_REP_2',
        'serviceResourceBackendIpAddress': '10.3.177.84',
        'nasType': 'ISCSI_REPLICANT',
        'createDate': '2017:50:15-04:00',
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

getReplicationPartners = [{
    'id': 1784,
    'accountId': 3000,
    'capacityGb': 20,
    'username': 'TEST_REP_1',
    'serviceResourceBackendIpAddress': '10.3.174.79',
    'nasType': 'ISCSI_REPLICANT',
    'hostId': None,
    'guestId': None,
    'hardwareId': None,
    'createDate': '2017:50:15-04:00',
    'serviceResource': {'datacenter': {'name': 'wdc01'}},
    'replicationSchedule': {'type': {'keyname': 'REPLICATION_HOURLY'}},
}, {
    'id': 1785,
    'accountId': 3001,
    'capacityGb': 20,
    'username': 'TEST_REP_2',
    'serviceResourceBackendIpAddress': '10.3.177.84',
    'nasType': 'ISCSI_REPLICANT',
    'hostId': None,
    'guestId': None,
    'hardwareId': None,
    'createDate': '2017:50:15-04:00',
    'serviceResource': {'datacenter': {'name': 'dal01'}},
    'replicationSchedule': {'type': {'keyname': 'REPLICATION_DAILY'}},
}]

getValidReplicationTargetDatacenterLocations = [{
    'id': 12345,
    'longName': 'Dallas 05',
    'name': 'dal05'
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
