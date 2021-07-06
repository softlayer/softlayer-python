getPrivateBlockDeviceTemplateGroups = [{
    'accountId': 1234,
    'blockDevices': [],
    'createDate': '2013-12-05T21:53:03-06:00',
    'globalIdentifier': 'E6DBD73B-1651-4B28-BCBA-A11DF7C9D79E',
    'id': 200,
    'name': 'test_image',
    'parentId': '',
    'publicFlag': False,
}, {
    'accountId': 1234,
    'blockDevices': [],
    'createDate': '2013-12-05T21:53:03-06:00',
    'globalIdentifier': 'F9329795-4220-4B0A-B970-C86B950667FA',
    'id': 201,
    # 'name': 'private_image2',
    'name': u'a¬ሴ€耀',
    'parentId': '',
    'publicFlag': False,
}]

getVirtualGuests = [{
    'id': 100,
    'metricTrackingObjectId': 1,
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
}, {
    'id': 104,
    'metricTrackingObjectId': 2,
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
    'virtualRack': {'id': 1, 'bandwidthAllotmentTypeId': 2},
}]

getMonthlyVirtualGuests = [vs for vs in getVirtualGuests
                           if not vs['hourlyBillingFlag']]
getHourlyVirtualGuests = [vs for vs in getVirtualGuests
                          if vs['hourlyBillingFlag']]

getHardware = [{
    'id': 1000,
    'metricTrackingObject': {'id': 3},
    'globalIdentifier': '1a2b3c-1701',
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
    "virtualHost": {
        "accountId": 11111,
        "id": 22222,
        "name": "vmware.chechu.com",
        "guests": [
            {
                "accountId": 11111,
                "createDate": "2019-09-05T17:03:42-06:00",
                "hostname": "NSX-T Manager",
                "id": 33333,
                "maxCpu": 16,
                "maxCpuUnits": "CORE",
                "maxMemory": 49152,
                "powerState": {
                    "keyName": "RUNNING",
                    "name": "Running"
                },
                "status": {
                    "keyName": "ACTIVE",
                    "name": "Active"
                }
            }]}
}, {
    'id': 1001,
    'metricTrackingObject': {'id': 4},
    'globalIdentifier': '1a2b3c-1702',
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
    "virtualHost": {
        "accountId": 11111,
        "id": 22222,
        "name": "host14.vmware.chechu.com",
        "guests": []
    }
}, {
    'id': 1002,
    'metricTrackingObject': {'id': 5},
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
    "virtualHost": {
        "accountId": 11111,
        "id": 22222,
        "name": "host14.vmware.chechu.com",
        "guests": []
    }
}, {
    'id': 1003,
    "virtualHost": {
        "accountId": 11111,
        "id": 22222,
        "name": "host14.vmware.chechu.com",
        "guests": []
    }
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
    ],
    'accountId': 1234
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
        'cidr': '/24',
        'networkVlanId': 123,
        'datacenter': {'name': 'dal00'},
        'version': 4,
        'subnetType': 'PRIMARY',
        'ipAddressCount': 10,
        'virtualGuests': [],
        'hardware': [],
        "podName": "dal05.pod04",
        "networkVlan": {
            "accountId": 123,
            "id": 2581232,
            "modifyDate": "2019-07-17T01:09:51+08:00",
            "vlanNumber": 795
        }
    },
    {
        "gateway": "5.111.11.111",
        "id": '111',
        "modifyDate": "2018-07-24T17:14:57+08:00",
        'networkIdentifier': '10.0.0.1',
        'ipAddressCount': 10,
        'cidr': '/24',
        'virtualGuests': [],
        'hardware': [],
        "networkVlanId": 22222,
        "sortOrder": "2",
        "subnetType": "SECONDARY_ON_VLAN",
        "totalIpAddresses": "8",
        "usableIpAddressCount": "5",
        "version": 4
    }
]

getSshKeys = [{'id': '100', 'label': 'Test 1'},
              {'id': '101', 'label': 'Test 2',
               'finterprint': 'aa:bb:cc:dd',
               'notes': 'my key'}]

getSecurityCertificates = [{'certificate': '1234',
                            'commonName': 'cert',
                            'id': 1234,
                            'validityDays': 0, }]
getExpiredSecurityCertificates = getSecurityCertificates
getValidSecurityCertificates = getSecurityCertificates

getTickets = [
    {
        "accountId": 1234,
        "serviceProviderResourceId": "CS123456",
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
        "serviceProviderResourceId": "CS123456",
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
        "serviceProviderResourceId": "CS123456",
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
        'assignedUser': {'firstName': 'John', 'lastName': 'Smith'},
        "statusId": 1001,
        "title": "Cloud Instance Cancellation - 08/01/13"
    }]

getOpenTickets = [ticket for ticket in getTickets
                  if ticket['statusId'] == 1001]
getClosedTickets = [ticket for ticket in getTickets
                    if ticket['statusId'] == 1002]

getCurrentUser = {'id': 12345, 'username': 'testAccount',
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
    'networkSpace': 'PRIVATE',
    'hardwareCount': 0,
    'hardware': [],
    'vlanNumber': 12,
    'networkComponents': [],
    'primaryRouter': {
        'datacenter': {'name': 'dal00'}
    },
    'virtualGuestCount': 0,
    'virtualGuests': [],
    'dedicatedFirewallFlag': True,
    'highAvailabilityFirewallFlag': True,
    'networkVlanFirewall': {'id': 1234},
    'totalPrimaryIpAddressCount': 1,
    'subnetCount': 0,
    'subnets': [],
    'firewallInterfaces': [
        {
            'id': 1,
            'name': 'outside'
        },
        {
            'id': 12,
            'name': 'inside'
        }
    ]
}, {
    'id': 2,
    'networkSpace': 'PRIVATE',
    'totalPrimaryIpAddressCount': 2,
    'dedicatedFirewallFlag': False,
    'highAvailabilityFirewallFlag': True,
    'networkVlanFirewall': {'id': 7896},
    'hardwareCount': 0,
    'hardware': [],
    'vlanNumber': 13,
    'networkComponents': [],
    'primaryRouter': {
        'datacenter': {'name': 'dal00'}
    },
    'virtualGuestCount': 0,
    'virtualGuests': [],
    'firewallGuestNetworkComponents': [{
        'id': 1234,
        'guestNetworkComponent': {'guest': {'id': 1}},
        'status': 'ok'}],
    'firewallNetworkComponents': [{
        'id': 1234,
        'networkComponent': {'downlinkComponent': {'hardwareId': 1}},
        'status': 'ok'}],
    'firewallInterfaces': [],

    'subnetCount': 0,
    'subnets': [],
}, {
    'id': 3,
    'networkSpace': 'PRIVATE',
    'name': 'dal00',
    'hardwareCount': 1,
    'dedicatedFirewallFlag': True,
    'highAvailabilityFirewallFlag': True,
    'networkVlanFirewall': {'id': 23456},
    'vlanNumber': 14,
    'hardware': [{'id': 1}],
    'networkComponents': [{'id': 2}],
    'primaryRouter': {
        'datacenter': {'name': 'dal00'}
    },
    'firewallInterfaces': [
        {
            'id': 31,
            'name': 'outside'
        }],
    'totalPrimaryIpAddressCount': 3,
    'subnetCount': 0,
    'subnets': [],
    'virtualGuestCount': 1,
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
    'storageType': {'keyName': 'ENDURANCE_STORAGE'},
    'fileNetworkMountAddress': '127.0.0.1:/TEST',
}]

getActiveQuotes = [{
    'accountId': 1234,
    'id': 1234,
    'name': 'TestQuote1234',
    'quoteKey': '1234test4321',
    'createDate': '2019-04-10T14:26:03-06:00',
    'modifyDate': '2019-04-10T14:26:03-06:00',
    'order': {
        'id': 37623333,
        'items': [
            {
                'categoryCode': 'guest_core',
                'description': '4 x 2.0 GHz or higher Cores',
                'id': 468394713,
                'itemId': 859,
                'itemPriceId': '1642',
                'oneTimeAfterTaxAmount': '0',
                'oneTimeFee': '0',
                'oneTimeFeeTaxRate': '0',
                'oneTimeTaxAmount': '0',
                'quantity': 1,
                'recurringAfterTaxAmount': '0',
                'recurringFee': '0',
                'recurringTaxAmount': '0',
                'setupAfterTaxAmount': '0',
                'setupFee': '0',
                'setupFeeDeferralMonths': None,
                'setupFeeTaxRate': '0',
                'setupTaxAmount': '0',
                'package': {'id': 46, 'keyName': 'CLOUD_SERVER'}
            },
        ]
    }
}]

getOrders = [{
    'id': 1234,
    'resourceType': '1 x 2.0 GHz Core',
    'hostName': 'test',
    'createDate': '2014-05-01T14:03:04-07:00',
    'cost': 0.0
}]

getBillingInfo = [{
    'id': 1234,
    'accountId': 123,
    'resourceType': '1 x 2.0 GHz Core',
    'hostName': 'test',
    'modifyDate': '2014-05-01T14:03:04-07:00',
    'createDate': '2014-05-01T14:03:04-07:00',
    'anniversaryDayOfMonth': 2,
    'percentDiscountOnetime': 2,
    'sparePoolAmount': 0,
    'currency': {
        'KeyName': 'usd',
        'id': 1,
        'name': 'dollars'
    }
}]

getLatestBillDate = '2014-05-01T14:03:04-07:00'

getBalance = 40

getNextInvoiceTotalAmount = 2

getHubNetworkStorage = [{'id': 12345, 'username': 'SLOS12345-1', 'serviceResource': {'name': 'Cleversafe - US Region'}},
                        {'id': 12346, 'username': 'SLOS12345-2', 'vendorName': 'Swift'}]

getIscsiNetworkStorage = [{
    'accountId': 1234,
    'billingItem': {'id': 449},
    'capacityGb': 20,
    'createDate': '2015:50:15-04:00',
    'guestId': '',
    'hardwareId': '',
    'hostId': '',
    'id': 100,
    'nasType': 'ISCSI',
    'notes': """{'status': 'available'}""",
    'password': '',
    'serviceProviderId': 1,
    'serviceResource': {'datacenter': {'name': 'dal05', 'id': 449500}},
    'serviceResourceBackendIpAddress': '10.1.2.3',
    'serviceResourceName': 'Storage Type 01 Aggregate staaspar0101_pc01',
    'username': 'username',
    'storageType': {'keyName': 'ENDURANCE_STORAGE'},
}]

getVirtualDedicatedRacks = [{
    'id': 1,
    'name': 'my first pool',
    'metricTrackingObjectId': 10,
}]

getDedicatedHosts = [{
    'datacenter': {
        'name': 'dal05'
    },
    'memoryCapacity': 242,
    'name': 'test-dedicated',
    'diskCapacity': 1200,
    'guestCount': 1,
    'cpuCount': 56,
    'id': 12345
}]

getUsers = [
    {'displayName': 'ChristopherG',
     'hardwareCount': 138,
     'id': 11100,
     'userStatus': {'name': 'Active'},
     'username': 'SL1234',
     'virtualGuestCount': 99,
     'externalBindingCount': 1,
     'apiAuthenticationKeyCount': 1,
     },
    {'displayName': 'PulseL',
     'hardwareCount': 100,
     'id': 11111,
     'userStatus': {'name': 'Active'},
     'username': 'sl1234-abob',
     'virtualGuestCount': 99,
     }
]

getReservedCapacityGroups = [
    {
        'accountId': 1234,
        'backendRouterId': 1411193,
        'createDate': '2018-09-24T16:33:09-06:00',
        'id': 3103,
        'modifyDate': '',
        'name': 'test-capacity',
        'availableInstanceCount': 1,
        'instanceCount': 3,
        'occupiedInstanceCount': 1,
        'backendRouter': {
            'accountId': 1,
            'bareMetalInstanceFlag': 0,
            'domain': 'softlayer.com',
            'fullyQualifiedDomainName': 'bcr02a.dal13.softlayer.com',
            'hardwareStatusId': 5,
            'hostname': 'bcr02a.dal13',
            'id': 1411193,
            'notes': '',
            'provisionDate': '',
            'serviceProviderId': 1,
            'serviceProviderResourceId': '',
            'primaryIpAddress': '10.0.144.28',
            'datacenter': {
                'id': 1854895,
                'longName': 'Dallas 13',
                'name': 'dal13',
                'statusId': 2
            },
            'hardwareFunction': {
                'code': 'ROUTER',
                'description': 'Router',
                'id': 1
            },
            'topLevelLocation': {
                'id': 1854895,
                'longName': 'Dallas 13',
                'name': 'dal13',
                'statusId': 2
            }
        },
        'instances': [
            {
                'id': 3501,
                'billingItem': {
                    'description': 'B1.1x2 (1 Year Term)',
                    'hourlyRecurringFee': '.032'
                }
            },
            {
                'id': 3519,
                'billingItem': {
                    'description': 'B1.1x2 (1 Year Term)',
                    'hourlyRecurringFee': '.032'
                }
            },
            {
                'id': 3519
            }
        ]
    }
]

getPlacementGroups = [{
    "createDate": "2019-01-18T16:08:44-06:00",
    "id": 12345,
    "name": "test01",
    "guestCount": 0,
    "backendRouter": {
        "hostname": "bcr01a.mex01",
        "id": 329266
    },
    "rule": {
        "id": 1,
        "keyName": "SPREAD",
        "name": "SPREAD"
    }
}]

getInvoices = [
    {
        'id': 33816665,
        'modifyDate': '2019-03-04T00:17:42-06:00',
        'createDate': '2019-03-04T00:17:42-06:00',
        'startingBalance': '129251.73',
        'statusCode': 'OPEN',
        'typeCode': 'RECURRING',
        'itemCount': 3317,
        'invoiceTotalAmount': '6230.66'
    },
    {
        'id': 12345667,
        'modifyDate': '2019-03-05T00:17:42-06:00',
        'createDate': '2019-03-04T00:17:42-06:00',
        'startingBalance': '129251.73',
        'statusCode': 'OPEN',
        'typeCode': 'RECURRING',
        'itemCount': 12,
        'invoiceTotalAmount': '6230.66',
        'endingBalance': '12345.55'
    }
]

getApplicationDeliveryControllers = [
    {
        'accountId': 307608,
        'createDate': '2015-05-05T16:23:52-06:00',
        'id': 11449,
        'modifyDate': '2015-05-05T16:24:09-06:00',
        'name': 'SLADC307608-1',
        'typeId': 2,
        'description': 'Citrix NetScaler VPX 10.5 10Mbps Standard',
        'managementIpAddress': '10.11.11.112',
        'outboundPublicBandwidthUsage': '.00365',
        'primaryIpAddress': '19.4.24.16',
        'datacenter': {
            'longName': 'Dallas 9',
            'name': 'dal09',
        },
        'password': {
            'password': 'aaaaa',
            'username': 'root'
        },
        'type': {
            'keyName': 'NETSCALER_VPX',
            'name': 'NetScaler VPX'
        }
    }
]

getScaleGroups = [
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
        },
        "virtualGuestMemberCount": 0,
        "status": {
            "id": 1,
            "keyName": "ACTIVE",
            "name": "Active"
        },
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
        }
    }
]

getPortableStorageVolumes = [
    {
        "capacity": 200,
        "createDate": "2018-10-06T04:27:59-06:00",
        "description": "Disk 2",
        "id": 11111,
        "modifyDate": "",
        "name": "Disk 2",
        "parentId": "",
        "storageRepositoryId": 22222,
        "typeId": 241,
        "units": "GB",
        "uuid": "fd477feb-bf32-408e-882f-02540gghgh111"
    }
]
getAllTopLevelBillingItems = [
    {
        "allowCancellationFlag": 1,
        "cancellationDate": "None",
        "categoryCode": "server",
        "createDate": "2015-05-28T09:53:41-06:00",
        "cycleStartDate": "2020-04-03T23:12:04-06:00",
        "description": "Dual E5-2690 v3 (12 Cores, 2.60 GHz)",
        "domainName": "sl-netbase.com",
        "hostName": "testsangeles101",
        "id": 53891943,
        "lastBillDate": "2020-04-03T23:12:04-06:00",
        "modifyDate": "2020-04-03T23:12:07-06:00",
        "nextBillDate": "2020-05-03T23:00:00-06:00",
        "orderItemId": 68626055,
        "parentId": "None",
        "recurringFee": "1000",
        "recurringFeeTaxRate": "0",
        "recurringMonths": 1,
        "hourlyFlag": False,
        "location": {
            "id": 265592,
            "longName": "Amsterdam 1",
            "name": "ams01",
            "statusId": 2
        },
        "nextInvoiceTotalRecurringAmount": 0,
        "orderItem": {
            "id": 68626055,
            "order": {
                "id": 4544893,
                "userRecord": {
                    "displayName": "TEst",
                    "email": "test@us.ibm.com",
                    "id": 167758,
                    "userStatus": {
                        "id": 1001,
                        "keyName": "CANCEL_PENDING",
                        "name": "Cancel Pending"
                    }
                }
            }
        },
        "resourceTableId": 544444
    },
    {
        "allowCancellationFlag": 1,
        "cancellationDate": "None",
        "categoryCode": "server",
        "createDate": "2015-05-28T09:56:44-06:00",
        "cycleStartDate": "2020-04-03T23:12:05-06:00",
        "description": "Dual E5-2690 v3 (12 Cores, 2.60 GHz)",
        "domainName": "sl-netbase.com",
        "hostName": "testsangeles101",
        "id": 53892197,
        "lastBillDate": "2020-04-03T23:12:05-06:00",
        "modifyDate": "2020-04-03T23:12:07-06:00",
        "nextBillDate": "2020-05-03T23:00:00-06:00",
        "orderItemId": 68626801,
        "recurringFee": "22220",
        "hourlyFlag": False,
        "location": {
            "id": 265592,
            "longName": "Amsterdam 1",
            "name": "ams01",
            "statusId": 2
        },
        "nextInvoiceTotalRecurringAmount": 0,
        "orderItem": {
            "id": 68626801,
            "order": {
                "id": 4545911,
                "userRecord": {
                    "displayName": "Test",
                    "email": "test@us.ibm.com",
                    "id": 167758,
                    "userStatus": {
                        "id": 1001,
                        "keyName": "ACTIVE",
                        "name": "Active"
                    }
                }
            }
        },
        "resourceTableId": 777777
    }
]

getNetworkStorage = [
    {
        "accountId": 1111111,
        "capacityGb": 20,
        "createDate": "2016-01-21T12:11:07-06:00",
        "id": 1234567,
        "nasType": "ISCSI",
        "username": "SL01SEL301234-11",
    },
    {
        "accountId": 1111111,
        "capacityGb": 20,
        "createDate": "2015-04-29T07:55:55-06:00",
        "id": 4917123,
        "nasType": "NAS",
        "username": "SL01SEV1234567_111"
    }
]

getRouters = [
    {
        "accountId": 1,
        "bareMetalInstanceFlag": 0,
        "domain": "softlayer.com",
        "fullyQualifiedDomainName": "fcr01a.ams01.softlayer.com",
        "hardwareStatusId": 5,
        "hostname": "fcr01a.ams01",
        "id": 123456,
        "serviceProviderId": 1,
        "topLevelLocation": {
            "id": 265592,
            "longName": "Amsterdam 1",
            "name": "ams01",
            "statusId": 2
        }
    }]

getNetworkStorage = [
    {
        "accountId": 1111111,
        "capacityGb": 20,
        "createDate": "2016-01-21T12:11:07-06:00",
        "id": 1234567,
        "nasType": "ISCSI",
        "username": "SL01SEL301234-11",
    },
    {
        "accountId": 1111111,
        "capacityGb": 20,
        "createDate": "2015-04-29T07:55:55-06:00",
        "id": 4917123,
        "nasType": "NAS",
        "username": "SL01SEV1234567_111"
    }
]

getNetworkMessageDeliveryAccounts = [
    {
        "accountId": 147258,
        "createDate": "2020-07-06T10:29:11-06:00",
        "id": 1232123,
        "typeId": 21,
        "username": "test_CLI@ie.ibm.com",
        "vendorId": 1,
        "type": {
            "description": "Delivery of messages through e-mail",
            "id": 21,
            "keyName": "EMAIL",
            "name": "Email"
        },
        "vendor": {
            "id": 1,
            "keyName": "SENDGRID",
            "name": "SendGrid"
        },
        "emailAddress": "test_CLI@ie.ibm.com",
        "smtpAccess": "1"
    }
]

getActiveAccountLicenses = [{
    "accountId": 123456,
    "capacity": "4",
    "key": "Y8GNS-7QRNG-OUIJO-MATEI-5GJRM",
    "units": "CPU",
    "billingItem": {
        "allowCancellationFlag": 1,
        "categoryCode": "software_license",
        "cycleStartDate": "2021-06-03T23:11:22-06:00",
        "description": "vCenter Server Appliance 6.0",
        "id": 741258963,
        "laborFee": "0",
        "laborFeeTaxRate": "0",
        "oneTimeFee": "0",
        "oneTimeFeeTaxRate": "0",
        "orderItemId": 963258741,
        "recurringFee": "0",
        "recurringFeeTaxRate": "0",
        "recurringMonths": 1,
        "serviceProviderId": 1,
        "setupFee": "0",
        "setupFeeTaxRate": "0"
    },
    "softwareDescription": {
        "controlPanel": 0,
        "id": 15963,
        "licenseTermValue": 0,
        "longDescription": "VMware vCenter 6.0",
        "manufacturer": "VMware",
        "name": "vCenter",
        "operatingSystem": 0,
        "version": "6.0",
        "virtualLicense": 0,
        "virtualizationPlatform": 0,
        "requiredUser": "administrator@vsphere.local"
    }
},
    {
        "accountId": 123456,
        "capacity": "4",
        "key": "TSZES-SJF85-04GLD-AXA64-8O1EO",
        "units": "CPU",
        "billingItem": {
            "allowCancellationFlag": 1,
            "categoryCode": "software_license",
            "description": "vCenter Server Appliance 6.x",
            "id": 36987456,
            "laborFee": "0",
            "laborFeeTaxRate": "0",
            "oneTimeFee": "0",
            "oneTimeFeeTaxRate": "0",
            "orderItemId": 25839,
            "recurringFee": "0",
            "recurringFeeTaxRate": "0",
            "recurringMonths": 1,
            "serviceProviderId": 1,
            "setupFee": "0",
            "setupFeeTaxRate": "0"
        },
        "softwareDescription": {
            "controlPanel": 0,
            "id": 1472,
            "licenseTermValue": 0,
            "longDescription": "VMware vCenter 6.0",
            "manufacturer": "VMware",
            "name": "vCenter",
            "operatingSystem": 0,
            "version": "6.0",
            "virtualLicense": 0,
            "virtualizationPlatform": 0,
            "requiredUser": "administrator@vsphere.local"
        }
    }
]

getActiveVirtualLicenses = [{
    "id": 12345,
    "ipAddress": "192.168.23.78",
    "key": "TEST.60220734.0000",
    "billingItem": {
        "categoryCode": "control_panel",
        "description": "Plesk Onyx (Linux) - (Unlimited) - VPS "
    },
    "softwareDescription": {
        "longDescription": "Plesk - Unlimited Domain w/ Power Pack for VPS 17.8.11 Linux",
        "manufacturer": "Plesk",
        "name": "Plesk - Unlimited Domain w/ Power Pack for VPS"
    },
    "subnet": {
        "broadcastAddress": "192.168.23.79",
        "cidr": 28,
        "gateway": "192.168.23.65",
        "id": 1973163,
        "isCustomerOwned": False,
        "isCustomerRoutable": False,
        "netmask": "255.255.255.240",
        "networkIdentifier": "128.116.23.64",
        "networkVlanId": 123456,
        "note": "test note",
        "sortOrder": "1",
        "subnetType": "ADDITIONAL_PRIMARY",
        "totalIpAddresses": "16",
        "usableIpAddressCount": "13",
        "version": 4
    }
}]
