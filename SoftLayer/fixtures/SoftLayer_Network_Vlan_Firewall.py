createCancelServerTicket = {'id': 1234, 'title': 'Server Cancellation Request'}
getObject = {
    "administrativeBypassFlag": "",
    "customerManagedFlag": False,
    "billingItem": {
        "id": 21370815
    },
    "id": 3130,
    "primaryIpAddress": "192.155.239.146",
    "datacenter": {
        "id": 265592,
        "longName": "Amsterdam 1",
        "name": "ams01",
        "statusId": 2
    },
    "networkVlan": {
        "accountId": 307608,
        "id": 371028,
        "primarySubnetId": 536252,
        "name": 'testvlan',
        "vlanNumber": 1489,
        "firewallInterfaces": [
            {
                "id": 6254,
                "name": "inside",
                "firewallContextAccessControlLists": [
                    {
                        "direction": "out",
                        "firewallContextInterfaceId": 6257,
                        "id": 3143
                    }
                ]
            },
            {
                "id": 6256,
                "name": "outside",
                "firewallContextAccessControlLists": [
                    {
                        "direction": "out",
                        "firewallContextInterfaceId": 6257,
                        "id": 3143
                    },
                    {
                        "direction": "in",
                        "firewallContextInterfaceId": 6256,
                        "id": 3142
                    }
                ]
            }
        ]
    },
    "rules": [
        {'destinationIpAddress': 'any on server',
         'protocol': 'tcp',
         'orderValue': 1,
         'destinationIpSubnetMask': '255.255.255.255',
         'destinationPortRangeStart': 80,
         'sourceIpSubnetMask': '0.0.0.0',
         'destinationPortRangeEnd': 80,
         'version': 4,
         'action': 'permit',
         'sourceIpAddress': '0.0.0.0'
         },
        {
            'destinationIpAddress': 'any on server',
            'protocol': 'tcp',
            'orderValue': 2,
            'destinationIpSubnetMask': '255.255.255.255',
            'destinationPortRangeStart': 1,
            'sourceIpSubnetMask': '255.255.255.255',
            'destinationPortRangeEnd': 65535,
            'version': 4,
            'action': 'permit',
            'sourceIpAddress': '193.212.1.10'
        },
        {
            'destinationIpAddress': 'any on server',
            'protocol': 'tcp',
            'orderValue': 3,
            'destinationIpSubnetMask': '255.255.255.255',
            'destinationPortRangeStart': 80,
            'sourceIpSubnetMask': '0.0.0.0',
            'destinationPortRangeEnd': 800,
            'version': 4,
            'action': 'permit',
            'sourceIpAddress': '0.0.0.0'
        }
    ]

}

getRules = [
    {
        'destinationIpAddress': 'any on server',
        'protocol': 'tcp',
        'orderValue': 1,
        'destinationIpSubnetMask': '255.255.255.255',
        'destinationPortRangeStart': 80,
        'sourceIpSubnetMask': '0.0.0.0',
        'destinationPortRangeEnd': 80,
        'version': 4,
        'action': 'permit',
        'sourceIpAddress': '0.0.0.0'
    },
    {
        'destinationIpAddress': 'any on server',
        'protocol': 'tmp',
        'orderValue': 2,
        'destinationIpSubnetMask': '255.255.255.255',
        'destinationPortRangeStart': 1,
        'sourceIpSubnetMask': '255.255.255.255',
        'destinationPortRangeEnd': 65535,
        'version': 4,
        'action': 'permit',
        'sourceIpAddress': '193.212.1.10'
    },
    {
        'destinationIpAddress': 'any on server',
        'protocol': 'tcp',
        'orderValue': 3,
        'destinationIpSubnetMask': '255.255.255.255',
        'destinationPortRangeStart': 80,
        'sourceIpSubnetMask': '0.0.0.0',
        'destinationPortRangeEnd': 800,
        'version': 4,
        'action': 'permit',
        'sourceIpAddress': '0.0.0.0'
    }
]
edit = True
