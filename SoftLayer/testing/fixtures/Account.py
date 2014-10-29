getPrivateBlockDeviceTemplateGroups = [{
    'accountId': 1234,
    'blockDevices': [],
    'createDate': '2013-12-05T21:53:03-06:00',
    'globalIdentifier': 'E6DBD73B-1651-4B28-BCBA-A11DF7C9D79E',
    'id': 200,
    'name': 'test_image',
    'parentId': ''
}, {
    'accountId': 1234,
    'blockDevices': [],
    'createDate': '2013-12-05T21:53:03-06:00',
    'globalIdentifier': 'F9329795-4220-4B0A-B970-C86B950667FA',
    'id': 201,
    'name': 'private_image2',
    'parentId': ''
}]

getVirtualGuests = [{
    'id': 100,
    'hostname': 'vs-test1',
    'domain': 'test.sftlyr.ws',
    'fullyQualifiedDomainName': 'vs-test1.test.sftlyr.ws',
    'status': {'keyName': 'ACTIVE', 'name': 'Active'},
    'datacenter': {'id': 50, 'name': 'TEST00',
                   'description': 'Test Data Center'},
    'powerState': {'keyName': 'RUNNING', 'name': 'Running'},
    'maxCpu': 2,
    'maxMemory': 1024,
    'primaryIpAddress': '172.16.240.2',
    'globalIdentifier': '1a2b3c-1701',
    'primaryBackendIpAddress': '10.45.19.37',
    'hourlyBillingFlag': False,
    'billingItem': {
        'id': 6327,
        'recurringFee': 1.54,
        'orderItem': {
            'order': {
                'userRecord': {
                    'username': 'chechu',
                }
            }
        }
    },
    'networkMonitors': [{
        'guestId': 100,
        'hardwareId': '',
        'lastResult': {'responseStatus': 2}
    }],
}, {
    'id': 104,
    'hostname': 'vs-test2',
    'domain': 'test.sftlyr.ws',
    'fullyQualifiedDomainName': 'vs-test2.test.sftlyr.ws',
    'status': {'keyName': 'ACTIVE', 'name': 'Active'},
    'datacenter': {'id': 50, 'name': 'TEST00',
                   'description': 'Test Data Center'},
    'powerState': {'keyName': 'RUNNING', 'name': 'Running'},
    'maxCpu': 4,
    'maxMemory': 4096,
    'primaryIpAddress': '172.16.240.7',
    'globalIdentifier': '05a8ac-6abf0',
    'primaryBackendIpAddress': '10.45.19.35',
    'hourlyBillingFlag': True,
    'billingItem': {
        'id': 6327,
        'recurringFee': 1.54,
        'orderItem': {
            'order': {
                'userRecord': {
                    'username': 'chechu',
                }
            }
        }
    },
    'networkMonitors': [{
        'guestId': 104,
        'hardwareId': '',
        'lastResult': {'responseStatus': 0}
    }],
}]

getMonthlyVirtualGuests = [vs for vs in getVirtualGuests
                           if not vs['hourlyBillingFlag']]
getHourlyVirtualGuests = [vs for vs in getVirtualGuests
                          if vs['hourlyBillingFlag']]


getHardware = [{
    'id': 1000,
    'datacenter': {'id': 50, 'name': 'TEST00',
                   'description': 'Test Data Center'},
    'billingItem': {
        'id': 6327,
        'recurringFee': 1.54,
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
    'fullyQualifiedDomainName': 'hardware-test1.test.sftlyr.ws',
    'processorPhysicalCoreAmount': 2,
    'memoryCapacity': 2,
    'primaryBackendIpAddress': '10.1.0.2',
    'networkManagementIpAddress': '10.1.0.3',
    'hardwareStatus': {'status': 'ACTIVE'},
    'provisionDate': '2013-08-01 15:23:45',
    'notes': 'These are test notes.',
    'operatingSystem': {
        'softwareLicense': {
            'softwareDescription': {
                'referenceCode': 'Ubuntu',
                'name': 'Ubuntu 12.04 LTS',
            }
        },
        'passwords': [
            {'username': 'root', 'password': 'abc123'}
        ],
    },
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
    },
    'networkMonitors': [{
        'guestId': '',
        'hardwareId': 1000,
        'lastResult': {'responseStatus': 2}
    }],
}, {
    'id': 1001,
    'datacenter': {'name': 'TEST00',
                   'description': 'Test Data Center'},
    'billingItem': {
        'id': 7112,
        'orderItem': {
            'order': {
                'userRecord': {
                    'username': 'chechu',
                }
            }
        }
    },
    'primaryIpAddress': '172.16.4.94',
    'hostname': 'hardware-test2',
    'domain': 'test.sftlyr.ws',
    'fullyQualifiedDomainName': 'hardware-test2.test.sftlyr.ws',
    'processorPhysicalCoreAmount': 4,
    'memoryCapacity': 4,
    'primaryBackendIpAddress': '10.1.0.3',
    'hardwareStatus': {'status': 'ACTIVE'},
    'provisionDate': '2013-08-03 07:15:22',
    'operatingSystem': {
        'softwareLicense': {
            'softwareDescription': {
                'referenceCode': 'Ubuntu',
                'name': 'Ubuntu 12.04 LTS',
            }
        }
    },
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
    'networkMonitors': [{
        'guestId': '',
        'hardwareId': 1001,
        'lastResult': {'responseStatus': 0}
    }],
}, {
    'id': 1002,
    'datacenter': {'name': 'TEST00',
                   'description': 'Test Data Center'},
    'billingItem': {
        'id': 7112,
        'orderItem': {
            'order': {
                'userRecord': {
                    'username': 'chechu',
                }
            }
        }
    },
    'primaryIpAddress': '172.16.4.95',
    'hostname': 'hardware-bad-memory',
    'domain': 'test.sftlyr.ws',
    'fullyQualifiedDomainName': 'hardware-bad-memory.test.sftlyr.ws',
    'processorPhysicalCoreAmount': 4,
    'memoryCapacity': None,
    'primaryBackendIpAddress': '10.1.0.4',
    'hardwareStatus': {'status': 'ACTIVE'},
    'provisionDate': '2014-04-02 13:48:00',
    'operatingSystem': {
        'softwareLicense': {
            'softwareDescription': {
                'referenceCode': 'Ubuntu',
                'name': 'Ubuntu 12.04 LTS',
            }
        }
    },
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
    'networkMonitors': [{
        'guestId': '',
        'hardwareId': 1002,
        'lastResult': {'responseStatus': 2}
    }],
}]
getDomains = [{'name': 'example.com',
               'id': 12345,
               'serial': 2014030728,
               'updateDate': '2014-03-07T13:52:31-06:00'}]

getObject = {
    'cdnAccounts': [
        {
            "cdnAccountName": "1234a",
            "providerPortalAccessFlag": False,
            "createDate": "2012-06-25T14:05:28-07:00",
            "id": 1234,
            "legacyCdnFlag": False,
            "dependantServiceFlag": True,
            "cdnSolutionName": "ORIGIN_PULL",
            "statusId": 4,
            "accountId": 1234
        },
        {
            "cdnAccountName": "1234a",
            "providerPortalAccessFlag": False,
            "createDate": "2012-07-24T13:34:25-07:00",
            "id": 1234,
            "legacyCdnFlag": False,
            "dependantServiceFlag": False,
            "cdnSolutionName": "POP_PULL",
            "statusId": 4,
            "accountId": 1234
        }
    ]
}

getRwhoisData = {
    'abuseEmail': 'abuseEmail',
    'accountId': 1234,
    'address1': 'address1',
    'address2': 'address2',
    'city': 'city',
    'companyName': 'companyName',
    'country': 'country',
    'createDate': 'createDate',
    'firstName': 'firstName',
    'id': 'id',
    'lastName': 'lastName',
    'modifyDate': 'modifyDate',
    'postalCode': 'postalCode',
    'privateResidenceFlag': True,
}

getGlobalIpRecords = [{
    'id': '200',
    'ipAddress': {
        'subnet': {
            'networkIdentifier': '10.0.0.1',
        },
        'ipAddress': '127.0.0.1',
    },
    'destinationIpAddress': {
        'ipAddress': '127.0.0.1',
        'virtualGuest': {'fullyQualifiedDomainName': 'example.com'}}
}, {
    'id': '201',
    'ipAddress': {
        'subnet': {
            'networkIdentifier': '10.0.0.1',
        },
        'ipAddress': '127.0.0.1',
    },
    'destinationIpAddress': {
        'ipAddress': '127.0.0.1',
        'hardware': {'fullyQualifiedDomainName': 'example.com'}}
}]

getSubnets = [
    {
        'id': '100',
        'networkIdentifier': '10.0.0.1',
        'datacenter': {'name': 'dal00'},
        'version': 4,
        'subnetType': 'PRIMARY'
    }]

getSshKeys = [{'id': '100', 'label': 'Test 1'},
              {'id': '101', 'label': 'Test 2',
               'finterprint': 'aa:bb:cc:dd',
               'notes': 'my key'}]

getSecurityCertificates = [{'certificate': '1234',
                            'commonName': 'cert',
                            'id': 1234}]
getExpiredSecurityCertificates = getSecurityCertificates
getValidSecurityCertificates = getSecurityCertificates

getTickets = [
    {
        "accountId": 1234,
        "assignedUserId": 12345,
        "createDate": "2013-08-01T14:14:04-07:00",
        "id": 100,
        "lastEditDate": "2013-08-01T14:16:47-07:00",
        "lastEditType": "AUTO",
        "modifyDate": "2013-08-01T14:16:47-07:00",
        "status": {
            "id": 1002,
            "name": "Closed"
        },
        "statusId": 1002,
        "title": "Cloud Instance Cancellation - 08/01/13"
    },
    {
        "accountId": 1234,
        "assignedUserId": 12345,
        "createDate": "2013-08-01T14:14:04-07:00",
        "id": 101,
        "lastEditDate": "2013-08-01T14:16:47-07:00",
        "lastEditType": "AUTO",
        "modifyDate": "2013-08-01T14:16:47-07:00",
        "status": {
            "id": 1002,
            "name": "Closed"
        },
        "statusId": 1002,
        "title": "Cloud Instance Cancellation - 08/01/13"
    },
    {
        "accountId": 1234,
        "assignedUserId": 12345,
        "createDate": "2014-03-03T09:44:01-08:00",
        "id": 102,
        "lastEditDate": "2013-08-01T14:16:47-07:00",
        "lastEditType": "AUTO",
        "modifyDate": "2014-03-03T09:44:03-08:00",
        "status": {
            "id": 1001,
            "name": "Open"
        },
        "statusId": 1001,
        "title": "Cloud Instance Cancellation - 08/01/13"
    }]

getOpenTickets = [ticket for ticket in getTickets
                  if ticket['statusId'] == 1001]
getClosedTickets = [ticket for ticket in getTickets
                    if ticket['statusId'] == 1002]

getCurrentUser = {'id': 12345,
                  'apiAuthenticationKeys': [{'authenticationKey': 'A' * 64}]}

getCdnAccounts = [
    {
        "cdnAccountName": "1234a",
        "providerPortalAccessFlag": False,
        "createDate": "2012-06-25T14:05:28-07:00",
        "id": 1234,
        "legacyCdnFlag": False,
        "dependantServiceFlag": True,
        "cdnSolutionName": "ORIGIN_PULL",
        "statusId": 4,
        "accountId": 1234
    },
    {
        "cdnAccountName": "1234a",
        "providerPortalAccessFlag": False,
        "createDate": "2012-07-24T13:34:25-07:00",
        "id": 1234,
        "legacyCdnFlag": False,
        "dependantServiceFlag": False,
        "cdnSolutionName": "POP_PULL",
        "statusId": 4,
        "accountId": 1234
    }
]

getNetworkVlans = [{
    'id': 1,
    'hardware': [],
    'networkComponents': [],
    'primaryRouter': {
        'datacenter': {'name': 'dal00'}
    },
    'virtualGuests': [],
    'dedicatedFirewallFlag': True,
    'highAvailabilityFirewallFlag': True,
    'networkVlanFirewall': {'id': 1234},
    'totalPrimaryIpAddressCount': 1,
    'subnets': [],
}, {
    'id': 2,
    'totalPrimaryIpAddressCount': 2,
    'dedicatedFirewallFlag': False,
    'hardware': [],
    'networkComponents': [],
    'primaryRouter': {
        'datacenter': {'name': 'dal00'}
    },
    'virtualGuests': [],
    'firewallGuestNetworkComponents': [{
        'id': 1234,
        'guestNetworkComponent': {'guest': {'id': 1}},
        'status': 'ok'}],
    'firewallNetworkComponents': [{
        'id': 1234,
        'networkComponent': {'downlinkComponent': {'hardwareId': 1}},
        'status': 'ok'}],
    'subnets': [],
}, {
    'id': 3,
    'name': 'dal00',
    'hardware': [{'id': 1}],
    'networkComponents': [{'id': 2}],
    'primaryRouter': {
        'datacenter': {'name': 'dal00'}
    },
    'totalPrimaryIpAddressCount': 3,
    'subnets': [],
    'virtualGuests': [{'id': 3}]
}]

getAdcLoadBalancers = []

getNasNetworkStorage = [{
    'id': 1,
    'capacityGb': 10,
    'serviceResource': {'datacenter': {'name': 'Dallas'}},
    'username': 'user',
    'password': 'pass',
    'serviceResourceBackendIpAddress': '127.0.0.1',
}]

getActiveQuotes = [{
    'id': 1234,
    'name': 'TestQuote1234',
    'quoteKey': '1234test4321',
}]
