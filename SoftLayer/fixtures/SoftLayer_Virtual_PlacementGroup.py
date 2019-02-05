getAvailableRouters = [{
    "accountId": 1,
    "fullyQualifiedDomainName": "bcr01.dal01.softlayer.com",
    "hostname": "bcr01.dal01",
    "id": 1,
    "topLevelLocation": {
        "id": 3,
        "longName": "Dallas 1",
        "name": "dal01",
    }
}]

createObject = {
    "accountId": 123,
    "backendRouterId": 444,
    "createDate": "2019-01-18T16:08:44-06:00",
    "id": 5555,
    "modifyDate": None,
    "name": "test01",
    "ruleId": 1
}
getObject = {
    "createDate": "2019-01-17T14:36:42-06:00",
    "id": 1234,
    "name": "test-group",
    "backendRouter": {
        "hostname": "bcr01a.mex01",
        "id": 329266
    },
    "guests": [{
        "accountId": 123456789,
        "createDate": "2019-01-17T16:44:46-06:00",
        "domain": "test.com",
        "fullyQualifiedDomainName": "issues10691547765077.test.com",
        "hostname": "issues10691547765077",
        "id": 69131875,
        "maxCpu": 1,
        "maxMemory": 1024,
        "placementGroupId": 1234,
        "provisionDate": "2019-01-17T16:47:17-06:00",
        "activeTransaction": {
            "id": 107585077,
            "transactionStatus": {
                "friendlyName": "TESTING TXN",
                "name": "RECLAIM_WAIT"
            }
        },
        "globalIdentifier": "c786ac04-b612-4649-9d19-9662434eeaea",
        "primaryBackendIpAddress": "10.131.11.14",
        "primaryIpAddress": "169.57.70.180",
        "status": {
            "keyName": "DISCONNECTED",
            "name": "Disconnected"
        }
    }],
    "rule": {
        "id": 1,
        "keyName": "SPREAD",
        "name": "SPREAD"
    }
}

deleteObject = True
