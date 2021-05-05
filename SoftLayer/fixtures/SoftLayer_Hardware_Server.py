getObject = {
    'id': 1000,
    'globalIdentifier': '1a2b3c-1701',
    'datacenter': {'id': 50, 'name': 'TEST00',
                   'description': 'Test Data Center'},
    'billingItem': {
        'id': 6327,
        'recurringFee': 1.54,
        'package': {
            'id': 911
        },
        'nextInvoiceTotalRecurringAmount': 16.08,
        'children': [
            {'description': 'test', 'nextInvoiceTotalRecurringAmount': 1},
        ],
        'nextInvoiceChildren': [
            {'description': 'test', 'nextInvoiceTotalRecurringAmount': 1, 'categoryCode': 'disk1'},
            {'description': 'test2', 'nextInvoiceTotalRecurringAmount': 2, 'categoryCode': 'disk3'}
        ],
        'orderItem': {
            'order': {
                'userRecord': {
                    'username': 'chechu',
                }
            }
        }
    },
    'primaryIpAddress': '172.16.1.100',
    'hostname': 'hardware-test1',
    'domain': 'test.sftlyr.ws',
    'bareMetalInstanceFlag': True,
    'fullyQualifiedDomainName': 'hardware-test1.test.sftlyr.ws',
    'processorPhysicalCoreAmount': 2,
    'memoryCapacity': 2,
    'primaryBackendIpAddress': '10.1.0.2',
    'networkManagementIpAddress': '10.1.0.3',
    'hardwareStatus': {'status': 'ACTIVE'},
    'primaryNetworkComponent': {'maxSpeed': 10, 'speed': 10},
    'provisionDate': '2013-08-01 15:23:45',
    'notes': 'These are test notes.',
    'operatingSystem': {
        'softwareLicense': {
            'softwareDescription': {
                'referenceCode': 'UBUNTU_12_64',
                'name': 'Ubuntu',
                'version': 'Ubuntu 12.04 LTS',
            }
        },
        'passwords': [
            {'username': 'root', 'password': 'abc123'}
        ],
    },
    'remoteManagementAccounts': [
        {'username': 'root', 'password': 'abc123'}
    ],
    'networkVlans': [
        {
            'networkSpace': 'PRIVATE',
            'vlanNumber': 1800,
            'id': 9653
        },
        {
            'networkSpace': 'PUBLIC',
            'vlanNumber': 3672,
            'id': 19082
        },
    ],
    'tagReferences': [
        {'tag': {'name': 'test_tag'}}
    ],
    'activeTransaction': {
        'transactionStatus': {
            'name': 'TXN_NAME',
            'friendlyName': 'Friendly Transaction Name',
            'id': 6660
        }
    }
}
editObject = True
setTags = True
setPrivateNetworkInterfaceSpeed = True
setPublicNetworkInterfaceSpeed = True
toggleManagementInterface = True
powerOff = True
powerOn = True
powerCycle = True
rebootSoft = True
rebootDefault = True
rebootHard = True
createFirmwareUpdateTransaction = True
createFirmwareReflashTransaction = True
setUserMetadata = ['meta']
reloadOperatingSystem = 'OK'
getReverseDomainRecords = [
    {'resourceRecords': [{'data': '2.0.1.10.in-addr.arpa'}]}]
bootToRescueLayer = True
getFrontendNetworkComponents = [
    {'maxSpeed': 100},
    {
        'maxSpeed': 1000,
        'networkComponentGroup': {
            'groupTypeId': 2,
            'networkComponents': [{'maxSpeed': 1000}, {'maxSpeed': 1000}]
        }
    },
    {
        'maxSpeed': 1000,
        'networkComponentGroup': {
            'groupTypeId': 2,
            'networkComponents': [{'maxSpeed': 1000}, {'maxSpeed': 1000}]
        }
    },
    {
        'maxSpeed': 1000,
        'networkComponentGroup': {
            'groupTypeId': 2,
            'networkComponents': [{'maxSpeed': 1000}, {'maxSpeed': 1000}]
        }
    },
    {
        'maxSpeed': 1000,
        'networkComponentGroup': {
            'groupTypeId': 2,
            'networkComponents': [{'maxSpeed': 1000}, {'maxSpeed': 1000}]
        }
    }
]

getBandwidthAllotmentDetail = {
    'allocationId': 25465663,
    'bandwidthAllotmentId': 138442,
    'effectiveDate': '2019-04-03T23:00:00-06:00',
    'endEffectiveDate': None,
    'id': 25888247,
    'serviceProviderId': 1,
    'allocation': {
        'amount': '250'
    }
}

getBillingCycleBandwidthUsage = [
    {
        'amountIn': '.448',
        'amountOut': '.52157',
        'type': {
            'alias': 'PUBLIC_SERVER_BW'
        }
    },
    {
        'amountIn': '.03842',
        'amountOut': '.01822',
        'type': {
            'alias': 'PRIVATE_SERVER_BW'
        }
    }
]

getMetricTrackingObjectId = 1000

getAttachedNetworkStorages = [
    {
        "accountId": 11111,
        "capacityGb": 20,
        "createDate": "2018-04-05T05:15:49-06:00",
        "id": 22222,
        "nasType": "NAS",
        "serviceProviderId": 1,
        "storageTypeId": "13",
        "username": "SL02SEV311111_11",
        "allowedHardware": [
            {
                "id": 12345,
                "datacenter": {
                    "id": 449506,
                    "longName": "Frankfurt 2",
                    "name": "fra02",
                    "statusId": 2
                }
            }
        ],
        "serviceResourceBackendIpAddress": "fsn-fra0201a-fz.service.softlayer.com",
        "serviceResourceName": "Storage Type 02 File Aggregate stfm-fra0201a"
    },
    {
        "accountId": 11111,
        "capacityGb": 12000,
        "createDate": "2018-01-28T04:57:30-06:00",
        "id": 3777111,
        "nasType": "ISCSI",
        "notes": "BlockStorage12T",
        "password": "",
        "serviceProviderId": 1,
        "storageTypeId": "7",
        "username": "SL02SEL32222-9",
        "allowedHardware": [
            {
                "id": 629222,
                "datacenter": {
                    "id": 449506,
                    "longName": "Frankfurt 2",
                    "name": "fra02",
                    "statusId": 2
                }
            }
        ],
        "serviceResourceBackendIpAddress": "10.31.95.152",
        "serviceResourceName": "Storage Type 02 Block Aggregate stbm-fra0201a"
    }
]

getAllowedHost = {
    "accountId": 11111,
    "credentialId": 22222,
    "id": 33333,
    "name": "iqn.2020-03.com.ibm:sl02su11111-v62941551",
    "resourceTableId": 6291111,
    "resourceTableName": "VIRTUAL_GUEST",
    "credential": {
        "accountId": "11111",
        "createDate": "2020-03-20T13:35:47-06:00",
        "id": 44444,
        "nasCredentialTypeId": 2,
        "password": "SjFDCpHrjskfj",
        "username": "SL02SU11111-V62941551"
    }
}

getHardDrives = [
    {
        "id": 11111,
        "serialNumber": "z1w4sdf",
        "serviceProviderId": 1,
        "hardwareComponentModel": {
            "capacity": "1000",
            "description": "SATAIII:2000:8300:Constellation",
            "id": 111,
            "manufacturer": "Seagate",
            "name": "Constellation ES",
            "hardwareGenericComponentModel": {
                "capacity": "1000",
                "units": "GB",
                "hardwareComponentType": {
                    "id": 1,
                    "keyName": "HARD_DRIVE",
                    "type": "Hard Drive",
                    "typeParentId": 5
                }
            }
        }
    }
]

getVirtualHost = {
    "accountId": 11111,
    "createDate": "2018-10-08T10:54:48-06:00",
    "description": "host16.vmware.chechu.com",
    "hardwareId": 22222,
    "id": 33333,
    "name": "host16.vmware.chechu.com",
    "uuid": "00000000-0000-0000-0000-0cc11111",
    "hardware": {
        "accountId": 11111,
        "domain": "chechu.com",
        "hostname": "host16.vmware",
        "id": 22222,
        "hardwareStatus": {
            "id": 5,
            "status": "ACTIVE"
        }
    }
}

getUpgradeItemPrices = [
    {
        "id": 21525,
        "recurringFee": "0",
        "categories": [
            {
                "categoryCode": "port_speed",
                "id": 26,
                "name": "Uplink Port Speeds",
            }
        ],
        "item": {
            "capacity": "10000",
            "description": "10 Gbps Redundant Public & Private Network Uplinks",
            "id": 4342,
            "keyName": "10_GBPS_REDUNDANT_PUBLIC_PRIVATE_NETWORK_UPLINKS"
        }
    },
    {
        "hourlyRecurringFee": ".247",
        "id": 209391,
        "recurringFee": "164",
        "categories": [
            {
                "categoryCode": "ram",
                "id": 3,
                "name": "RAM"
            }
        ],
        "item": {
            "capacity": "32",
            "description": "32 GB RAM",
            "id": 11291,
            "keyName": "RAM_32_GB_DDR4_2133_ECC_NON_REG"
        }
    },
    {
        "hourlyRecurringFee": ".068",
        "id": 22482,
        "recurringFee": "50",
        "categories": [
            {
                "categoryCode": "disk_controller",
                "id": 11,
                "name": "Disk Controller",
            }
        ],
        "item": {
            "capacity": "0",
            "description": "RAID",
            "id": 4478,
            "keyName": "DISK_CONTROLLER_RAID",
        }
    },
    {
        "id": 50357,
        "recurringFee": "0",
        "categories": [
            {
                "categoryCode": "bandwidth",
                "id": 10,
                "name": "Public Bandwidth",
            }
        ],
        "item": {
            "capacity": "500",
            "description": "500 GB Bandwidth Allotment",
            "id": 6177,
            "keyName": "BANDWIDTH_500_GB"
        }
    },
    {
        "hourlyRecurringFee": ".023",
        "id": 49759,
        "recurringFee": "15",
        "categories": [
            {
                "categoryCode": "disk2",
                "id": 6,
                "name": "Third Hard Drive"
            }
        ],
        "item": {
            "capacity": "1000",
            "description": "1.00 TB SATA",
            "id": 6159,
            "keyName": "HARD_DRIVE_1_00_TB_SATA_2",
        }
    },
    {
        "id": 49759,
        "recurringFee": "0",
        "categories": [
            {
                "categoryCode": "disk1",
                "id": 5,
                "name": "Second Hard Drive"
            }
        ],
        "item": {
            "capacity": "1000",
            "description": "1.00 TB SATA",
            "id": 6159,
            "keyName": "HARD_DRIVE_1_00_TB_SATA_2"
        }
    }
]

getComponents = [{
    "hardwareComponentModelId": 147,
    "hardwareId": 1234,
    "id": 369,
    "modifyDate": "2017-11-10T16:59:38-06:00",
    "serviceProviderId": 1,
    "hardwareComponentModel": {
        "name": "IMM2 - Onboard",
        "firmwares": [
            {
                "createDate": "2020-09-24T13:46:29-06:00",
                "version": "5.60"
            },
            {
                "createDate": "2019-10-14T16:51:12-06:00",
                "version": "5.10"
            }]}}]
