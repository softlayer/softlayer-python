STAAS_TEST_VOLUME = {
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
        'categoryCode': 'storage_as_a_service',
        'hourlyFlag': None,
        'id': 454,
        'location': {'id': 449500}
    },
    'capacityGb': 500,
    'hasEncryptionAtRest': 1,
    'id': 102,
    'iops': 1000,
    'lunId': 2,
    'osType': {'keyName': 'LINUX'},
    'originalVolumeSize': '500',
    'parentVolume': {'snapshotSizeBytes': 1024},
    'provisionedIops': '1000',
    'replicationPartnerCount': 0,
    'schedules': [{
        'id': 978,
        'type': {'keyname': 'SNAPSHOT_WEEKLY'},
    }],
    'serviceResource': {'datacenter': {'id': 449500, 'name': 'dal05'}},
    'serviceResourceBackendIpAddress': '10.1.2.3',
    'snapshotCapacityGb': '10',
    'staasVersion': '2',
    'storageTierLevel': 'READHEAVY_TIER',
    'storageType': {'keyName': 'ENDURANCE_BLOCK_STORAGE'},
    'username': 'duplicatable_volume_username'
}

getObject = {
    'accountId': 1234,
    'activeTransactionCount': 1,
    'activeTransactions': [{
        'transactionStatus': {'friendlyName': 'This is a buffer time in which the customer may cancel the server'}
    }],
    'allowedHardware': [{
        'allowedHost': {
            'credential': {'username': 'joe', 'password': '12345'},
            'name': 'test-server',
        },
        'domain': 'example.com',
        'hostname': 'test-server',
        'id': 1234,
        'primaryBackendIpAddress': '10.0.0.2',
    }],
    'allowedIpAddresses': [{
        'allowedHost': {
            'credential': {'username': 'joe', 'password': '12345'},
            'name': 'test-server',
        },
        'id': 1234,
        'ipAddress': '10.0.0.1',
        'note': 'backend ip',
    }],
    'allowedSubnets': [{
        'allowedHost': {
            'credential': {'username': 'joe', 'password': '12345'},
            'name': 'test-server',
        },
        'cidr': '24',
        'id': 1234,
        'networkIdentifier': '10.0.0.1',
        'note': 'backend subnet',
    }],
    'allowedVirtualGuests': [{
        'allowedHost': {
            'credential': {'username': 'joe', 'password': '12345'},
            'name': 'test-server',
        },
        'domain': 'example.com',
        'hostname': 'test-server',
        'id': 1234,
        'primaryBackendIpAddress': '10.0.0.1',
    }],
    'billingItem': {
        'activeChildren': [{
            'cancellationDate': '',
            'categoryCode': 'storage_snapshot_space',
            'id': 123,
        }],
        'cancellationDate': '',
        'categoryCode': 'storage_service_enterprise',
        'id': 449,
        'location': {'id': 449500}
    },
    'bytesUsed': 0,
    'capacityGb': 20,
    'createDate': '2015:50:15-04:00',
    'fileNetworkMountAddress': '127.0.0.1:/TEST',
    'guestId': '',
    'hardwareId': '',
    'hasEncryptionAtRest': 0,
    'hostId': '',
    'id': 100,
    'iops': 1000,
    'lunId': 2,
    'nasType': 'ISCSI',
    'notes': """{'status': 'available'}""",
    'originalSnapshotName': 'test-original-snapshot-name',
    'originalVolumeName': 'test-original-volume-name',
    'originalVolumeSize': '20',
    'osType': {'keyName': 'LINUX'},
    'parentVolume': {'snapshotSizeBytes': 1024},
    'password': '',
    'provisionedIops': '1000',
    'replicationPartnerCount': 1,
    'replicationPartners': [{
        'createDate': '2017:50:15-04:00',
        'id': 1784,
        'nasType': 'ISCSI_REPLICANT',
        'replicationSchedule': {'type': {'keyname': 'REPLICATION_HOURLY'}},
        'serviceResource': {'datacenter': {'name': 'wdc01'}},
        'serviceResourceBackendIpAddress': '10.3.174.79',
        'username': 'TEST_REP_1',
    }, {
        'createDate': '2017:50:15-04:00',
        'id': 1785,
        'nasType': 'ISCSI_REPLICANT',
        'replicationSchedule': {'type': {'keyname': 'REPLICATION_DAILY'}},
        'serviceResource': {'datacenter': {'name': 'dal01'}},
        'serviceResourceBackendIpAddress': '10.3.177.84',
        'username': 'TEST_REP_2',
    }],
    'replicationStatus': 'Replicant Volume Provisioning has completed.',
    'schedules': [
        {
            'id': 978,
            'type': {'keyname': 'SNAPSHOT_WEEKLY'},
            'properties': [
                {'type': {'keyname': 'MINUTE'}, 'value': '30'},
            ]
        },
        {
            'id': 988,
            'type': {'keyname': 'REPLICATION_INTERVAL'},
            'properties': [
                {'type': {'keyname': 'MINUTE'}, 'value': '-1'},
            ]
        }
    ],
    'serviceProviderId': 1,
    'serviceResource': {'datacenter': {'id': 449500, 'name': 'dal05'}},
    'serviceResourceBackendIpAddress': '10.1.2.3',
    'serviceResourceName': 'Storage Type 01 Aggregate staaspar0101_pc01',
    'snapshotCapacityGb': '10',
    'staasVersion': '1',
    'storageTierLevel': 'READHEAVY_TIER',
    'storageType': {'keyName': 'ENDURANCE_STORAGE'},
    'username': 'username',
    'dependentDuplicate': 1,
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

listVolumeSchedules = [
    {
        'id': 978,
        'type': {'keyname': 'SNAPSHOT_WEEKLY'},
        'properties': [{'type': {'keyname': 'MINUTE'}, 'value': '30'}]
    },
    {
        'id': 988,
        'type': {'keyname': 'REPLICATION_INTERVAL'},
        'properties': [{'type': {'keyname': 'MINUTE'}, 'value': '-1'}]
    }
]

deleteObject = True
editObject = True
allowAccessFromHostList = True
removeAccessFromHostList = True
failoverToReplicant = True
failbackFromReplicant = True
restoreFromSnapshot = True
disasterRecoveryFailoverToReplicant = True

createSnapshot = {
    'id': 449
}

enableSnapshots = True
disableSnapshots = True

getVolumeCountLimits = {
    'datacenterName': 'global',
    'maximumAvailableCount': 300,
    'provisionedCount': 100
}

refreshDuplicate = {
     'dependentDuplicate': 1
}

convertCloneDependentToIndependent = {
    'dependentDuplicate': 1
}
