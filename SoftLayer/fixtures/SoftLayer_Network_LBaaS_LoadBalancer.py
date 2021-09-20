getObject = {
    'accountId': 1234,
    'address': 'test-01-307608-ams01.clb.appdomain.cloud',
    'createDate': '2019-08-12T07:49:43-06:00',
    'id': 1111111,
    'isPublic': 0,
    'locationId': 265592,
    'modifyDate': '2019-08-13T16:26:06-06:00',
    'name': 'test-01',
    'operatingStatus': 'ONLINE',
    'provisioningStatus': 'ACTIVE',
    'type': 0,
    'useSystemPublicIpPool': 1,
    'uuid': '1a1aa111-4474-4e16-9f02-4de959229b85',
    'listenerCount': 4,
    'memberCount': 1,
    'previousErrorText': 'test',
    'datacenter': {
        'id': 265592,
        'longName': 'Amsterdam 1',
        'name': 'ams01',
        'statusId': 2
    },
    'healthMonitors': [
        {
            'createDate': '2019-08-20T18:05:09-04:00',
            'interval': 5,
            'maxRetries': 2,
            'modifyDate': '2019-08-20T18:05:18-04:00',
            'monitorType': 'HTTP',
            'provisioningStatus': 'ACTIVE',
            'timeout': 2,
            'urlPath': '/',
            'uuid': 'c11111c1-f5ab-4c15-ba96-d7b95dc7c824'
        }
    ],
    'l7Pools': [
        {
            'createDate': '2019-08-19T16:33:37-04:00',
            'id': 222222,
            'loadBalancingAlgorithm': 'ROUNDROBIN',
            'modifyDate': None,
            'name': 'test',
            'protocol': 'HTTP',
            'provisioningStatus': 'ACTIVE',
            'uuid': 'a1111111-c5e7-413f-9f78-84f6c5e1ca04'
        }
    ],
    'listeners': [
        {
            'clientTimeout': 15,
            'defaultPool': {
                'healthMonitor': {
                    'uuid': '222222ab-bbcc-4f32-9b31-1b6d3a1959c8'
                },
                'protocol': 'HTTP',
                'protocolPort': 256,
                'uuid': 'ab1a1abc-0e83-4690-b5d4-1359625dba8f',
            }
        },
        {
            'clientTimeout': 15,
            'defaultPool': {
                'healthMonitor': {
                    'uuid': '222222ab-bbcc-4f32-9b31-1b6d3a1959c0'
                },
                'protocol': 'HTTP',
                'protocolPort': 256,
                'uuid': 'ab1a1abc-0e83-4690-b5d4-1359625dba8x',
            }
        },
        {'connectionLimit': None,
         'createDate': '2019-08-21T17:19:25-04:00',
         'defaultPool': {'createDate': '2019-08-21T17:19:25-04:00',
                         'healthMonitor': {'createDate': '2019-08-21T17:17:04-04:00',
                                           'id': 859330,
                                           'interval': 5,
                                           'maxRetries': 2,
                                           'modifyDate': '2019-08-21T17:17:15-04:00',
                                           'monitorType': 'HTTP',
                                           'provisioningStatus': 'ACTIVE',
                                           'timeout': 2,
                                           'urlPath': '/',
                                           'uuid': '55e00152-75fd-4f94-9263-cb4c6e005f12'},
                         'loadBalancingAlgorithm': 'ROUNDROBIN',
                         'members': [{'address': '10.136.4.220',
                                      'createDate': '2019-08-12T09:49:43-04:00',
                                      'id': 1023118,
                                      'modifyDate': '2019-08-12T09:52:54-04:00',
                                      'provisioningStatus': 'ACTIVE',
                                      'uuid': 'ba23a166-faa4-4eb2-96e7-ef049d65ce60',
                                      'weight': 50}],
                         'modifyDate': '2019-08-21T17:19:33-04:00',
                         'protocol': 'HTTP',
                         'protocolPort': 230,
                         'provisioningStatus': 'ACTIVE',
                         'uuid': '1c5f3ba6-ec7d-4cf8-8815-9bb174224a76'},
         'id': 889072,
         'l7Policies': [{'action': 'REJECT',
                         'createDate': '2019-08-21T18:17:41-04:00',
                         'id': 215204,
                         'modifyDate': None,
                         'name': 'trestst',
                         'priority': 1,
                         'redirectL7PoolId': None,
                         'uuid': 'b8c30aae-3979-49a7-be8c-fb70e43a6b4b'}],
         'modifyDate': '2019-08-22T10:58:02-04:00',
         'protocol': 'HTTP',
         'protocolPort': 110,
         'provisioningStatus': 'ACTIVE',
         'tlsCertificateId': None,
         'clientTimeout': 30,
         'uuid': 'a509723d-a3cb-4ae4-bc5b-5ecf04f890ff'}
    ],
    'members': [
        {
            'address': '10.0.0.1',
            'createDate': '2019-08-12T09:49:43-04:00',
            'modifyDate': '2019-08-12T09:52:54-04:00',
            'provisioningStatus': 'ACTIVE',
            'uuid': 'ba23a166-faa4-4eb2-96e7-ef049d65ce60',
            'weight': 50
        }
    ],
    'sslCiphers': [
        {
            'id': 2, 'name': 'ECDHE-RSA-AES256-GCM-SHA384'
        }
    ],
}
getAllObjects = [getObject]

getLoadBalancer = {
    "accountId": 3071234,
    "createDate": "2019-08-12T21:49:43+08:00",
    "id": 81234,
    "isPublic": 0,
    "locationId": 265592,
    "modifyDate": "2019-08-14T06:26:06+08:00",
    "name": "dcabero-01",
    "uuid": "0a2da082-4474-4e16-9f02-4de11111",
    "datacenter": {
        "id": 265592,
        "longName": "Amsterdam 1",
        "name": "ams01",
        "statusId": 2
    }
}

cancelLoadBalancer = True

getLoadBalancerMemberHealth = [
    {
        'poolUuid': '1c5f3ba6-ec7d-4cf8-8815-9bb174224a76',
        'membersHealth': [
            {
                'status': 'DOWN',
                'uuid': 'ba23a166-faa4-4eb2-96e7-ef049d65ce60'
            }
        ]
    }
]

getHealthMonitors = {}

getLoadBalancer = getObject
cancelLoadBalancer = getObject
