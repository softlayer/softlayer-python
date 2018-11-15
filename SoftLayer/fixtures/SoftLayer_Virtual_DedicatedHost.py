getObject = {
    'id': 37401,
    'memoryCapacity': 242,
    'modifyDate': '',
    'name': 'test-dedicated',
    'diskCapacity': 1200,
    'createDate': '2017-10-16T12:50:23-05:00',
    'cpuCount': 56,
    'accountId': 1199911
}


getAvailableRouters = [
    {'hostname': 'bcr01a.dal05', 'id': 12345},
    {'hostname': 'bcr02a.dal05', 'id': 12346},
    {'hostname': 'bcr03a.dal05', 'id': 12347},
    {'hostname': 'bcr04a.dal05', 'id': 12348}
]

getObjectById = {
    'datacenter': {
        'id': 12345,
        'name': 'dal05',
        'longName': 'Dallas 5'
    },
    'memoryCapacity': 242,
    'modifyDate': '2017-11-06T11:38:20-06:00',
    'name': 'test-dedicated',
    'diskCapacity': 1200,
    'backendRouter': {
        'domain': 'test.com',
        'hostname': 'bcr01a.dal05',
        'id': 12345
    },
    'guestCount': 1,
    'cpuCount': 56,
    'guests': [{
        'domain': 'test.com',
        'hostname': 'test-dedicated',
        'id': 12345,
        'uuid': 'F9329795-4220-4B0A-B970-C86B950667FA'
    }],
    'billingItem': {
        'nextInvoiceTotalRecurringAmount': 1515.556,
        'orderItem': {
            'id': 12345,
            'order': {
                'status': 'APPROVED',
                'privateCloudOrderFlag': False,
                'modifyDate': '2017-11-02T11:42:50-07:00',
                'orderQuoteId': '',
                'userRecordId': 12345,
                'createDate': '2017-11-02T11:40:56-07:00',
                'impersonatingUserRecordId': '',
                'orderTypeId': 7,
                'presaleEventId': '',
                'userRecord': {
                    'username': 'test-dedicated'
                },
                'id': 12345,
                'accountId': 12345
            }
        },
        'id': 12345,
        'children': [
            {
                'nextInvoiceTotalRecurringAmount': 0.0,
                'categoryCode': 'dedicated_host_ram'
            },
            {
                'nextInvoiceTotalRecurringAmount': 0.0,
                'categoryCode': 'dedicated_host_disk'
            }
        ]
    },
    'id': 12345,
    'createDate': '2017-11-02T11:40:56-07:00'
}

deleteObject = True

getGuests = [{
    'id': 200,
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
    'id': 202,
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
    }
}]
