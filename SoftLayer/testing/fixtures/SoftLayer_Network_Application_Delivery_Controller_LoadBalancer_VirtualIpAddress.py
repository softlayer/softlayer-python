getBillingItem = {'id': 21370814}
getObject = {
    'accountId': 307608,
    'connectionLimit': 500,
    'connectionLimitUnits': "connections/second",
    'dedicatedFlag': False,
    'highAvailabilityFlag': False,
    'id': 22348,
    'ipAddressId': 7303278,
    'managedResourceFlag': False,
    'sslActiveFlag': False,
    'sslEnabledFlag': True,
    'virtualServers': [
        {
            'allocation': 10,
            'id': 50718,
            'port': 80,
            "serviceGroups": [
                {
                    'id': 51758,
                    'routingMethodId': 10,
                    'routingTypeId': 3,
                    'services': [
                        {
                            'enabled': 1,
                            'id': 1234,
                            'healthChecks': [
                                {
                                    'id': 112112
                                }
                            ],
                            'groupReferences': [
                                {
                                    'serviceGroupId': 51758,
                                    'serviceId': 84986,
                                    'weight': 2
                                }
                            ],
                            'ipAddressId': 14288108,
                            'port': 8080,
                            'status': "DOWN"
                        }
                    ]
                }
            ],
            "virtualIpAddress": {
                'accountId': 307608,
                'connectionLimit': 500,
                'connectionLimitUnits': "connections/second",
                'id': 22348,
                'ipAddressId': 7303278,
            },
            'virtualIpAddressId': 22348
        }]}
getVirtualServers = [
    {
        "allocation": 10,
        "id": 50718,
        "port": 80,
        "serviceGroups": [
            {
                "id": 51758,
                "routingMethodId": 10,
                "routingTypeId": 3,
                "services": [
                    {
                        "enabled": 1,
                        "id": 1234,
                        "healthChecks": [
                            {
                                "id": 112112
                            }
                        ],
                        "groupReferences": [
                            {
                                "serviceGroupId": 51758,
                                "serviceId": 84986,
                                "weight": 2
                            }
                        ],
                        "ipAddressId": 14288108,
                        "port": 8080,
                        "status": "DOWN"
                    }
                ]
            }
        ],
        "virtualIpAddress": {
            "accountId": 307608,
            "connectionLimit": 500,
            "connectionLimitUnits": "connections/second",
            "id": 22348,
            "ipAddressId": 7303278,
        },
        "virtualIpAddressId": 22348
    }
]
editObject = True
