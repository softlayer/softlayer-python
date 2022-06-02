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
    "firewallType": "fortigate-security-appliance-10gb",
    "managementCredentials": {
        "createDate": "2022-05-17T13:59:17-06:00",
        "id": 74604882,
        "modifyDate": "2022-05-17T13:59:17-06:00",
        "password": "test1234",
        "port": 23,
        "softwareId": 67804284,
        "username": "myusername"
    },
    "networkGateway": {
        "accountId": 307608,
        "groupNumber": 1,
        "id": 615448,
        "name": "testFirewall",
        "networkSpace": "BOTH",
        "privateIpAddressId": 188996652,
        "privateVlanId": 3228724,
        "publicIpAddressId": 188996794,
        "publicIpv6AddressId": 188996808,
        "publicVlanId": 3228726,
        "statusId": 1,
        "insideVlans": [],
        "members": [
            {
                "hardwareId": 3222842,
                "id": 687820,
                "networkGatewayId": 615448,
                "priority": 254,
                "networkGateway": None
            }
        ],
        "privateIpAddress": {
            "id": 188996652,
            "ipAddress": "10.37.115.70",
            "isBroadcast": False,
            "isGateway": False,
            "isNetwork": False,
            "isReserved": True,
            "subnetId": 2552734,
            "subnet": {
                "broadcastAddress": "10.37.115.127",
                "cidr": 26,
                "gateway": "10.37.115.65",
                "id": 2552734,
                "isCustomerOwned": False,
                "isCustomerRoutable": False,
                "modifyDate": "2022-05-17T13:59:16-06:00",
                "netmask": "255.255.255.192",
                "networkIdentifier": "10.37.115.64",
                "networkVlanId": 3228724,
                "sortOrder": "1",
                "subnetType": "ADDITIONAL_PRIMARY",
                "totalIpAddresses": "64",
                "usableIpAddressCount": "61",
                "version": 4
            }
        },
        "privateVlan": {
            "accountId": 307608,
            "fullyQualifiedName": "dal13.bcr03.1330",
            "id": 3228724,
            "modifyDate": "2022-05-17T14:01:14-06:00",
            "primarySubnetId": 2625456,
            "vlanNumber": 1330
        },
        "publicIpAddress": {
            "id": 188996794,
            "ipAddress": "67.228.206.245",
            "isBroadcast": False,
            "isGateway": False,
            "isNetwork": False,
            "isReserved": True,
            "subnetId": 66444,
            "subnet": {
                "broadcastAddress": "67.228.206.247",
                "cidr": 29,
                "gateway": "67.228.206.241",
                "id": 66444,
                "isCustomerOwned": False,
                "isCustomerRoutable": False,
                "modifyDate": "2022-05-17T13:59:16-06:00",
                "netmask": "255.255.255.248",
                "networkIdentifier": "67.228.206.240",
                "networkVlanId": 3228726,
                "sortOrder": "1",
                "subnetType": "ADDITIONAL_PRIMARY",
                "totalIpAddresses": "8",
                "usableIpAddressCount": "5",
                "version": 4
            }
        },
        "publicIpv6Address": {
            "id": 188996808,
            "ipAddress": "2607:f0d0:2703:0039:0000:0000:0000:0004",
            "isBroadcast": False,
            "isGateway": False,
            "isNetwork": False,
            "isReserved": True,
            "subnetId": 2547678,
            "subnet": {
                "broadcastAddress": "",
                "cidr": 64,
                "gateway": "2607:f0d0:2703:0039:0000:0000:0000:0001",
                "id": 2547678,
                "isCustomerOwned": False,
                "isCustomerRoutable": False,
                "modifyDate": "2022-05-17T13:59:16-06:00",
                "netmask": "ffff:ffff:ffff:ffff:0000:0000:0000:0000",
                "networkIdentifier": "2607:f0d0:2703:0039:0000:0000:0000:0000",
                "networkVlanId": 3228726,
                "sortOrder": "4",
                "subnetType": "PRIMARY_6",
                "totalIpAddresses": "18446744073709551616",
                "usableIpAddressCount": "18446744073709551614",
                "version": 6
            }
        },
        "publicVlan": {
            "accountId": 307608,
            "fullyQualifiedName": "dal13.fcr03.1255",
            "id": 3228726,
            "modifyDate": "2022-05-17T14:00:42-06:00",
            "primarySubnetId": 2623338,
            "vlanNumber": 1255
        },
        "status": {
            "description": "Gateway is ready to accept commands and actions",
            "id": 1,
            "keyName": "ACTIVE",
            "name": "Active"
        }
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
    ],
    "metricTrackingObject": {
        "id": 147258369,
        "resourceTableId": 17438,
        "startDate": "2022-05-17T14:01:48-06:00",
        "type": {
            "keyname": "FIREWALL_CONTEXT",
            "name": "Firewall Module Context"
        }
    }

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
