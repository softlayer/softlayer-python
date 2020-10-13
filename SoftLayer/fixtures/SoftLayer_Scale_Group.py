getObject = {
    'accountId': 31111,
    'balancedTerminationFlag': False,
    'cooldown': 1800,
    'createDate': '2018-04-30T15:07:40-04:00',
    'desiredMemberCount': None,
    'id': 12222222,
    'lastActionDate': '2019-10-02T16:26:17-04:00',
    'loadBalancers': [],
    'maximumMemberCount': 6,
    'minimumMemberCount': 2,
    'modifyDate': '2019-10-03T17:16:47-04:00',
    'name': 'tests',
    'networkVlans': [
        {
            'networkVlan': {
                'accountId': 31111,
                'id': 2222222,
                'modifyDate': '2019-07-16T13:09:47-04:00',
                'networkSpace': 'PRIVATE',
                'primaryRouter': {
                    'hostname': 'bcr01a.sao01'
                },
                'primarySubnetId': 1172222,
                'vlanNumber': 1111
            },
            'networkVlanId': 2281111
        }
    ],
    'policies': [
        {
            'actions': [
                {
                    'amount': 1,
                    'createDate': '2019-09-26T18:30:22-04:00',
                    'deleteFlag': None,
                    'id': 611111,
                    'modifyDate': None,
                    'scalePolicy': None,
                    'scalePolicyId': 681111,
                    'scaleType': 'RELATIVE',
                    'typeId': 1
                }
            ],
            'cooldown': None,
            'createDate': '2019-09-26T18:30:14-04:00',
            'id': 680000,
            'name': 'prime-poly',
            'scaleActions': [
                {
                    'amount': 1,
                    'createDate': '2019-09-26T18:30:22-04:00',
                    'deleteFlag': None,
                    'id': 633333,
                    'modifyDate': None,
                    'scalePolicy': None,
                    'scalePolicyId': 680123,
                    'scaleType': 'RELATIVE',
                    'typeId': 1
                }
            ],
            'triggers': [
                {
                    'createDate': '2019-09-26T18:30:14-04:00',
                    'deleteFlag': None,
                    'id': 557111,
                    'modifyDate': None,
                    'scalePolicy': None,
                    'scalePolicyId': 680000,
                    'typeId': 3
                }
            ]
        }
    ],
    'regionalGroup': {
        'description': 'sa-bra-south-1',
        'id': 663,
        'locationGroupTypeId': 42,
        'locations': [
            {
                'id': 983497,
                'longName': 'Sao Paulo 1',
                'name': 'sao01',
                'statusId': 2
            }
        ],
        'name': 'sa-bra-south-1',
        'securityLevelId': None
    },
    'regionalGroupId': 663,
    'status': {
        'id': 1, 'keyName': 'ACTIVE', 'name': 'Active'
    },
    'suspendedFlag': False,
    'terminationPolicy': {
        'id': 2, 'keyName': 'NEWEST', 'name': 'Newest'
    },
    'terminationPolicyId': 2,
    'virtualGuestAssets': [],
    'virtualGuestMemberCount': 6,
    'virtualGuestMemberTemplate': {
        'accountId': 31111,
        'blockDevices': [
            {
                'bootableFlag': None,
                'createDate': None,
                'device': '0',
                'diskImage': {
                    'capacity': 25,
                    'createDate': None,
                    'id': None,
                    'modifyDate': None,
                    'parentId': None,
                    'storageRepositoryId': None,
                    'typeId': None},
                'diskImageId': None,
                'guestId': None,
                'hotPlugFlag': None,
                'id': None,
                'modifyDate': None,
                'statusId': None
            },
            {
                'bootableFlag': None,
                'createDate': None,
                'device': '2',
                'diskImage': {
                    'capacity': 10,
                    'createDate': None,
                    'id': None,
                    'modifyDate': None,
                    'parentId': None,
                    'storageRepositoryId': None,
                    'typeId': None},
                'diskImageId': None,
                'guestId': None,
                'hotPlugFlag': None,
                'id': None,
                'modifyDate': None,
                'statusId': None
            }
        ],
        'createDate': None,
        'datacenter': {
            'id': None,
            'name': 'sao01',
            'statusId': None
        },
        'dedicatedAccountHostOnlyFlag': None,
        'domain': 'tech-support.com',
        'hostname': 'testing',
        'hourlyBillingFlag': True,
        'id': None,
        'lastPowerStateId': None,
        'lastVerifiedDate': None,
        'localDiskFlag': False,
        'maxCpu': None,
        'maxMemory': 1024,
        'metricPollDate': None,
        'modifyDate': None,
        'networkComponents': [
            {
                'createDate': None,
                'guestId': None,
                'id': None,
                'maxSpeed': 100,
                'modifyDate': None,
                'networkId': None,
                'port': None,
                'speed': None
            }
        ],
        'operatingSystemReferenceCode': 'CENTOS_LATEST',
        'placementGroupId': None,
        'postInstallScriptUri': 'https://test.com/',
        'privateNetworkOnlyFlag': False,
        'provisionDate': None,
        'sshKeys': [
            {
                'createDate': None,
                'id': 490279,
                'modifyDate': None
            }
        ],
        'startCpus': 1,
        'statusId': None,
        'typeId': None},
    'virtualGuestMembers': [
        {
            'id': 3111111,
            'virtualGuest': {

                'domain': 'tech-support.com',
                'hostname': 'test',
                'provisionDate': '2019-09-27T14:29:53-04:00'
            }
        }
    ]
}

getVirtualGuestMembers = getObject['virtualGuestMembers']

scale = [
    {
        "accountId": 31111,
        "cooldown": 1800,
        "createDate": "2016-10-25T01:48:34+08:00",
        "id": 12222222,
        "maximumMemberCount": 5,
        "minimumMemberCount": 0,
        "name": "tests",
        "virtualGuest": {
            "accountId": 31111,
            "createDate": "2019-10-02T15:24:54-06:00",
            "billingItem": {
                "cancellationDate": "2019-10-02T08:34:21-06:00"}
        },
        "virtualGuestMemberTemplate": {
            "accountId": 31111,
            "domain": "sodg.com",
            "hostname": "testing",
            "maxMemory": 32768,
            "startCpus": 32,
            "blockDevices": [
                {
                    "device": "0",
                    "diskImage": {
                        "capacity": 25,
                    }
                }
            ],
            "datacenter": {
                "name": "sao01",
            },
            "hourlyBillingFlag": True,
            "operatingSystemReferenceCode": "CENTOS_LATEST",
            "privateNetworkOnlyFlag": True
        },
        "virtualGuestMemberCount": 0,
        "status": {
            "id": 1,
            "keyName": "ACTIVE",
            "name": "Active"
        },
        "virtualGuestAssets": [],
        "virtualGuestMembers": []
    },
    {
        "accountId": 31111,
        "cooldown": 1800,
        "createDate": "2018-04-24T04:22:00+08:00",
        "id": 224533333,
        "maximumMemberCount": 10,
        "minimumMemberCount": 0,
        "modifyDate": "2019-01-19T04:53:21+08:00",
        "name": "test-ajcb",
        "virtualGuest": {
            "accountId": 31111,
            "createDate": "2019-10-02T15:24:54-06:00",
            "billingItem": {
                "cancellationDate": "2019-10-02T08:34:21-06:00"}
        },
        "virtualGuestMemberTemplate": {
            "accountId": 31111,
            "domain": "test.local",
            "hostname": "autoscale-ajcb01",
            "id": None,
            "maxCpu": None,
            "maxMemory": 1024,
            "postInstallScriptUri": "http://test.com",
            "startCpus": 1,
            "blockDevices": [
                {
                    "device": "0",
                    "diskImage": {
                        "capacity": 25,
                    }
                }
            ],
            "datacenter": {
                "name": "seo01",
            },
            "hourlyBillingFlag": True,
            "operatingSystemReferenceCode": "CENTOS_7_64",
        },
        "virtualGuestMemberCount": 0,
        "status": {
            "id": 1,
            "keyName": "ACTIVE",
            "name": "Active"
        },
        "virtualGuestAssets": [],
        "virtualGuestMembers": []
    }
]

scaleTo = [
    {
        "accountId": 31111,
        "cooldown": 1800,
        "createDate": "2016-10-25T01:48:34+08:00",
        "id": 12222222,
        "lastActionDate": "2016-10-25T01:48:34+08:00",
        "maximumMemberCount": 5,
        "minimumMemberCount": 0,
        "name": "tests",
        "regionalGroupId": 663,
        "virtualGuest": {
        },
        "virtualGuestMemberTemplate": {
            "accountId": 31111,
            "domain": "sodg.com",
            "hostname": "testing",
            "id": None,
            "maxCpu": None,
            "maxMemory": 32768,
            "startCpus": 32,
            "datacenter": {
                "name": "sao01",
            },
            "hourlyBillingFlag": True,
            "operatingSystemReferenceCode": "CENTOS_LATEST",
            "privateNetworkOnlyFlag": True
        },
        "virtualGuestMemberCount": 0,
        "status": {
            "id": 1,
            "keyName": "ACTIVE",
            "name": "Active"
        },
        "virtualGuestAssets": [],
        "virtualGuestMembers": []
    },
    {
        "accountId": 31111,
        "cooldown": 1800,
        "createDate": "2018-04-24T04:22:00+08:00",
        "id": 224533333,
        "lastActionDate": "2019-01-19T04:53:18+08:00",
        "maximumMemberCount": 10,
        "minimumMemberCount": 0,
        "modifyDate": "2019-01-19T04:53:21+08:00",
        "name": "test-ajcb",
        "regionalGroupId": 1025,
        "virtualGuest": {
            "accountId": 31111,
            "createDate": "2019-10-02T15:24:54-06:00",
            "billingItem": {
                "cancellationDate": "2019-10-02T08:34:21-06:00"}
        },
        "virtualGuestMemberTemplate": {
            "accountId": 31111,
            "domain": "test.local",
            "hostname": "autoscale-ajcb01",
            "id": None,
            "maxCpu": None,
            "maxMemory": 1024,
            "postInstallScriptUri": "http://test.com",
            "startCpus": 1,
            "blockDevices": [
                {
                    "device": "0",
                    "diskImage": {
                        "capacity": 25,
                    }
                }
            ],
            "datacenter": {
                "name": "seo01",
            },
            "hourlyBillingFlag": True,
            "operatingSystemReferenceCode": "CENTOS_7_64",
        },
        "virtualGuestMemberCount": 0,
        "status": {
            "id": 1,
            "keyName": "ACTIVE",
            "name": "Active"
        },
        "virtualGuestAssets": [],
        "virtualGuestMembers": []
    },
]

getLogs = [
    {
        "createDate": "2019-10-03T04:26:11+08:00",
        "description": "Scaling group to 6 member(s) by adding 3 member(s) as manually requested",
        "id": 3821111,
        "scaleGroupId": 2252222,
        "scaleGroup": {
            "accountId": 31111,
            "cooldown": 1800,
            "createDate": "2018-05-01T03:07:40+08:00",
            "id": 2251111,
            "lastActionDate": "2019-10-03T04:26:17+08:00",
            "maximumMemberCount": 6,
            "minimumMemberCount": 2,
            "modifyDate": "2019-10-03T04:26:21+08:00",
            "name": "ajcb-autoscale11",
            "regionalGroupId": 663,
            "terminationPolicyId": 2,
            "virtualGuestMemberTemplate": {
                "accountId": 31111,
                "domain": "techsupport.com",
                "hostname": "ajcb-autoscale22",
                "maxMemory": 1024,
                "postInstallScriptUri": "https://pastebin.com/raw/62wrEKuW",
                "startCpus": 1,
                "blockDevices": [
                    {
                        "device": "0",
                        "diskImage": {
                            "capacity": 25,
                        }
                    },
                    {
                        "device": "2",
                        "diskImage": {
                            "capacity": 10,
                        }
                    }
                ],
                "datacenter": {
                    "name": "sao01",
                },
                "networkComponents": [
                    {
                        "maxSpeed": 100,
                    }
                ],
                "operatingSystemReferenceCode": "CENTOS_LATEST",
                "sshKeys": [
                    {
                        "id": 49111,
                    }
                ]
            },
            "logs": [
                {
                    "createDate": "2019-09-28T02:31:35+08:00",
                    "description": "Scaling group to 3 member(s) by removing -1 member(s) as manually requested",
                    "id": 3821111,
                    "scaleGroupId": 2251111,
                },
                {
                    "createDate": "2019-09-28T02:26:11+08:00",
                    "description": "Scaling group to 4 member(s) by adding 2 member(s) as manually requested",
                    "id": 38211111,
                    "scaleGroupId": 2251111,
                },
            ]
        }
    },
]

editObject = True
