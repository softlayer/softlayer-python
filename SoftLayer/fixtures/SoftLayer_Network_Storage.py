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
    'serviceResource': {'datacenter': {'id': 449500, 'name': 'dal05'},
                        'name': 'Cleversafe - US Region',
                        'type': {
                            'type': 'CLEVERSAFE_SVC_API'
                        }},
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

getVolumeCountLimits = [{
    "datacenterName": "global",
    "maximumAvailableCount": 700,
    "provisionedCount": 2632
},
    {
        "maximumAvailableCount": 50,
        "provisionedCount": 2632
    },
    {
        "datacenterName": "dal13",
        "maximumAvailableCount": 52,
        "provisionedCount": 30
    },
]

refreshDuplicate = {
    'dependentDuplicate': 1
}

convertCloneDependentToIndependent = {
    'dependentDuplicate': 1
}

getDuplicateConversionStatus = {
    'activeConversionStartTime': '2023-01-01',
    'deDuplicateConversionPercentage': 50,
    'volumeUsername': 'testUser'
}

BLOCK_LIST_ISSUES_1732 = {
    'capacityGb': 16000,
    'id': 167214314,
    'notes': 'test',
    'username': 'SL02SEL307608-60',
    'activeTransactionCount': 0,
    'replicationPartnerCount': 1,
    'lunId': '1',
    'parentVolume': {
        'accountId': 307608,
        'capacityGb': 16000,
        'createDate': '2020-09-02T14:55:32-06:00',
        'guestId': None,
        'hardwareId': None,
        'hostId': None,
        'id': 167214302,
        'nasType': 'NAS_CONTAINER',
        'serviceProviderId': 1,
        'storageTypeId': '3',
        'upgradableFlag': True,
        'username': 'SL02SEVC307608_60',
        'serviceResourceBackendIpAddress': 'fsf-mex0101b-fz.service.softlayer.com',
        'serviceResourceName': 'Storage Type 02 Aggregate stxf-mex0101b',
        'snapshotSizeBytes': '831488'
    },
    'provisionedIops': '4096',
    'replicationPartners': [{
        'id': 167236648,
        'username': 'SL02SEL307608_60_REP_1',
        'replicationSchedule': {
            'active': 1,
            'createDate': '2020-09-02T17:10:04-06:00',
            'id': 542062,
            'modifyDate': None,
            'name': 'SL02SEVC307608_60_WEEKLY',
            'partnershipId': None,
            'typeId': 34,
            'volumeId': 167214302,
            'type': {
                'keyname': 'REPLICATION_WEEKLY'
            }
        },
        'serviceResource': {
            'backendIpAddress': 'fsf-sao0102c-fz.service.softlayer.com',
            'id': 30650,
            'name': 'Storage Type 02 Aggregate stxf-sao0102c',
            'datacenter': {
                'name': 'sao01'
            },
            'type': {
                'type': 'NETAPP_STOR_AGGR'
            }
        },
        'serviceResourceBackendIpAddress': '10.200.14.72'
    }],
    'replicationStatus': 'FAILBACK_COMPLETED',
    'serviceResource': {
        'backendIpAddress': 'fsf-mex0101b-fz.service.softlayer.com',
        'id': 9291,
        'name': 'Storage Type 02 Aggregate stxf-mex0101b',
        'datacenter': {
            'name': 'mex01'
        }
    },
    'serviceResourceBackendIpAddress': '10.2.190.99',
    'snapshotCapacityGb': '1000',
    'storageTierLevel': 'LOW_INTENSITY_TIER',
    'storageType': {
        'keyName': 'ENDURANCE_BLOCK_STORAGE'
    }
}


FILE_DETAIL_ISSUE2154 = {
    "capacityGb": 150,
    "id": 609491933,
    "username": "SL02SV1414935_187",
    "activeTransactionCount": 0,
    "replicationPartnerCount": 1,
    "fileNetworkMountAddress": "fsf-natestdal0505-fcb-fz.service.softlayer.com:/SL02SV1414935_187/data01",
    "originalVolumeSize": "20",
    "provisionedIops": "2000",
    "replicationStatus": "FAILOVER_COMPLETED",
    "serviceResourceBackendIpAddress": "fsf-natestdal0505-fcb-fz.service.softlayer.com",
    "snapshotCapacityGb": "5",
    "activeTransactions": [
        {
            "createDate": "",
            "elapsedSeconds": 111763,
            "guestId": "",
            "hardwareId": "",
            "id": "",
            "modifyDate": "",
            "statusChangeDate": "",
            "transactionGroup": {
                "name": "Volume Modification"
            },
            "transactionStatus": {
                "friendlyName": "In Progress"
            }
        }
    ],
    "parentVolume": {
        "accountId": 1414935,
        "capacityGb": 120,
        "createDate": "2024-05-16T02:28:02-05:00",
        "guestId": "",
        "hardwareId": "",
        "hostId": "",
        "id": 609491967,
        "nasType": "SNAPSHOT",
        "notes": "vol_duplicate_snapshot_2024-05-16_0228",
        "serviceProviderId": 1,
        "storageTypeId": "16",
        "upgradableFlag": True,
        "username": "SL02SV1414935_187",
        "serviceResourceBackendIpAddress": "fsf-natestdal0505-fcb-fz.service.softlayer.com",
        "serviceResourceName": "Storage Type 02 Aggregate natestdal0505-fc-d",
        "snapshotSizeBytes": "0"
    },
    "replicationPartners": [
        {
            "id": 609491945,
            "username": "SL02SV1414935_187_REP_1",
            "serviceResourceBackendIpAddress": "fsf-natestdal0505-ffb-fz.service.softlayer.com",
            "replicationSchedule": {
                "active": 1,
                "createDate": "2024-05-16T01:20:19-05:00",
                "id": 666339,
                "modifyDate": "",
                "name": "SL02SV1414935_187_HOURLY_REP",
                "partnershipId": "",
                "typeId": 32,
                "volumeId": 609491933,
                "type": {
                    "keyname": "REPLICATION_HOURLY"
                }
            },
            "serviceResource": {
                "backendIpAddress": "fsf-natestdal0505-ffb-fz.service.softlayer.com",
                "id": 57365,
                "name": "Storage Type 02 Aggregate natestdal0505-ff-d",
                "datacenter": {
                    "name": "dal10"
                },
                "type": {
                    "type": "NETAPP_STOR_AGGR"
                }
            }
        }
    ],
    "serviceResource": {
        "backendIpAddress": "fsf-natestdal0505-fcb-fz.service.softlayer.com",
        "id": 52292,
        "name": "Storage Type 02 Aggregate natestdal0505-fc-d",
        "attributes": [
            {
                "value": "2",
                "attributeType": {
                    "keyname": "STAAS_VERSION"
                }
            }
        ],
        "datacenter": {
            "name": "lon02"
        },
        "type": {
            "type": "NETAPP_STOR_AGGR"
        }
    },
    "storageType": {
        "keyName": "PERFORMANCE_FILE_STORAGE"
    }
}
