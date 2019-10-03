getObject = {
    "accountId": 31111,
    "cooldown": 1800,
    "createDate": "2016-10-25T01:48:34+08:00",
    "id": 12222222,
    "lastActionDate": "2016-10-25T01:48:34+08:00",
    "maximumMemberCount": 5,
    "minimumMemberCount": 0,
    "name": "tests",
    "regionalGroupId": 663,
    "virtualGuestMemberTemplate": {
        "accountId": 31111,
        "domain": "sodg.com",
        "hostname": "testing",
        "id": None,
        "maxCpu": None,
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
}

scale = [
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
        "virtualGuestMemberTemplate": {
            "accountId": 31111,
            "domain": "sodg.com",
            "hostname": "testing",
            "id": None,
            "maxCpu": None,
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
        "lastActionDate": "2019-01-19T04:53:18+08:00",
        "maximumMemberCount": 10,
        "minimumMemberCount": 0,
        "modifyDate": "2019-01-19T04:53:21+08:00",
        "name": "test-ajcb",
        "regionalGroupId": 1025,
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
        "virtualGuestMemberTemplate": {
            "accountId": 31111,
            "domain": "sodg.com",
            "hostname": "testing",
            "id": None,
            "maxCpu": None,
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
        "lastActionDate": "2019-01-19T04:53:18+08:00",
        "maximumMemberCount": 10,
        "minimumMemberCount": 0,
        "modifyDate": "2019-01-19T04:53:21+08:00",
        "name": "test-ajcb",
        "regionalGroupId": 1025,
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
