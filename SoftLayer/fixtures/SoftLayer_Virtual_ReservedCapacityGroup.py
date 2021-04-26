getObject = {
    'accountId': 1234,
    'backendRouterId': 1234567,
    "occupiedInstanceCount": 1,
    "availableInstanceCount": 0,
    'backendRouter': {
        'fullyQualifiedDomainName': 'bcr02a.dal13.softlayer.com',
        'hostname': 'bcr02a.dal13',
        'id': 1234567,
        'datacenter': {
            'id': 1854895,
            'longName': 'Dallas 13',
            'name': 'dal13',

        }
    },
    'createDate': '2018-09-24T16:33:09-06:00',
    'id': 100,
    'name': 'test-capacity',
    'instances': [
        {
            'createDate': '2018-09-24T16:33:09-06:00',
            'guestId': 111,
            'id': 1111,
            'billingItem': {
                'id': 1234,
                'recurringFee': '3.04',
                "description": "B1.2x4 (1 Year Term)",
                'category': {'name': 'Reserved Capacity'},
                'item': {
                    'keyName': 'B1_1X2_1_YEAR_TERM'
                }
            },
            'guest': {
                'domain': 'cgallo.com',
                'hostname': 'test-reserved-instance',
                'id': 111,
                'modifyDate': '2018-09-27T16:49:26-06:00',
                'primaryBackendIpAddress': '10.73.150.179',
                'primaryIpAddress': '169.62.147.165'
            }
        },
        {
            'createDate': '2018-09-24T16:33:10-06:00',
            'guestId': 1111,
            'id': 2222,
            'billingItem': {
                'id': 3333333,
                'recurringFee': '3.04',
                "description": "B1.2x4 (1 Year Term)",
                'category': {
                    'name': 'Reserved Capacity'
                },
                'item': {
                    'keyName': 'B1_1X2_1_YEAR_TERM'
                }
            }
        }
    ]
}

getObject_pending = {
    'accountId': 1234,
    'backendRouterId': 1111,
    'backendRouter': {
        'fullyQualifiedDomainName': 'bcr02a.dal13.softlayer.com',
        'hostname': 'bcr02a.dal13',
        'id': 1111,
        'datacenter': {
            'id': 1854895,
            'longName': 'Dallas 13',
            'name': 'dal13',

        }
    },
    'createDate': '2018-09-24T16:33:09-06:00',
    'id': 1111,
    'modifyDate': '',
    'name': 'test-capacity',
    'instances': [
        {
            'createDate': '2018-09-24T16:33:09-06:00',
            'guestId': 2222,
            'id': 1111,
        }
    ]
}

getInstances = [
    {
        "createDate": "2020-05-12T14:10:22-06:00",
        "guestId": 1234,
        "id": 123,
        "guest": {
            "accountId": 1234567,
            "createDate": "2020-05-12T14:10:22-06:00",
            "domain": "example.com",
            "fullyQualifiedDomainName": "reserved.example.com",
            "hostname": "reserved",
            "id": 1234,
            "maxCpu": 2,
            "maxCpuUnits": "CORE",
            "maxMemory": 4096,
            "modifyDate": "2020-05-14T13:37:09-06:00",
            "startCpus": 2,
            "statusId": 1001,
            "typeId": 1,
            "status": {
                "keyName": "ACTIVE",
                "name": "Active"
            }
        },
        "reservedCapacityGroup": {
            "accountId": 1234567,
            "createDate": "2020-05-12T14:10:22-06:00",
            "id": 1111,
            "modifyDate": "2021-04-16T14:59:09-06:00",
            "name": "test",
            "instancesCount": 1
        }
    }
]

editObject = True
