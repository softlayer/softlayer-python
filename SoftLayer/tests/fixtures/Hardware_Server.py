getObject = {
    'id': 1000,
    'datacenter': {'id': 50, 'name': 'TEST00',
                   'description': 'Test Data Center'},
    'billingItem': {'id': 6327, 'recurringFee': 1.54},
    'primaryIpAddress': '172.16.1.100',
    'hostname': 'hardware-test1',
    'domain': 'test.sftlyr.ws',
    'fullyQualifiedDomainName': 'hardware-test1.test.sftlyr.ws',
    'processorPhysicalCoreAmount': 2,
    'memoryCapacity': 2,
    'primaryBackendIpAddress': '10.1.0.2',
    'networkManagementIpAddress': '10.1.0.3',
    'hardwareStatus': {'status': 'ACTIVE'},
    "primaryNetworkComponent": {"speed": 10},
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
    }
}
editObject = True
setPrivateNetworkInterfaceSpeed = True
setPublicNetworkInterfaceSpeed = True
powerOff = True
powerOn = True
powerCycle = True
rebootSoft = True
rebootDefault = True
rebootHard = True
setUserMetadata = ['meta']
reloadOperatingSystem = 'OK'
getReverseDomainRecords = [
    {'resourceRecords': [{'data': '2.0.1.10.in-addr.arpa'}]}]
