getObject = {
    'id': 1234,
    'globalIdentifier': 'xxxxc-asd',
    'datacenter': {'id': 12, 'name': 'DALLAS21',
                   'description': 'Dallas 21'},
    'billingItem': {
        'id': 6327,
        'recurringFee': 1.54,
        'nextInvoiceTotalRecurringAmount': 16.08,
        'children': [
            {'description': 'test', 'nextInvoiceTotalRecurringAmount': 1},
        ],
        'orderItem': {
            'order': {
                'userRecord': {
                    'username': 'bob',
                }
            }
        }
    },
    'primaryIpAddress': '4.4.4.4',
    'hostname': 'testtest1',
    'domain': 'test.sftlyr.ws',
    'bareMetalInstanceFlag': True,
    'fullyQualifiedDomainName': 'testtest1.test.sftlyr.ws',
    'processorPhysicalCoreAmount': 4,
    'memoryCapacity': 4,
    'primaryBackendIpAddress': '10.4.4.4',
    'networkManagementIpAddress': '10.4.4.4',
    'hardwareStatus': {'status': 'ACTIVE'},
    'primaryNetworkComponent': {'maxSpeed': 1000, 'speed': 1000},
    'provisionDate': '2020-08-01 15:23:45',
    'notes': 'NOTES NOTES NOTES',
    'operatingSystem': {
        'softwareLicense': {
            'softwareDescription': {
                'referenceCode': 'UBUNTU_20_64',
                'name': 'Ubuntu',
                'version': 'Ubuntu 20.04 LTS',
            }
        },
        'passwords': [
            {'username': 'root', 'password': 'xxxxxxxxxxxx'}
        ],
    },
    'remoteManagementAccounts': [
        {'username': 'root', 'password': 'zzzzzzzzzzzzzz'}
    ],
    'networkVlans': [
        {
            'networkSpace': 'PRIVATE',
            'vlanNumber': 1234,
            'id': 11111
        },
    ],
    'tagReferences': [
        {'tag': {'name': 'a tag'}}
    ],
}

allowAccessToNetworkStorageList = True
