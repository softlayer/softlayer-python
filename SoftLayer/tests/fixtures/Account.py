
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
    'hostname': 'cci-test1',
    'domain': 'test.sftlyr.ws',
    'fullyQualifiedDomainName': 'cci-test1.test.sftlyr.ws',
    'status': {'keyName': 'ACTIVE', 'name': 'Active'},
    # TODO - This needs to come from wherever data centers come from
    'datacenter': {'id': 50, 'name': 'TEST00',
                   'description': 'Test Data Center'},
    'powerState': {'keyName': 'RUNNING', 'name': 'Running'},
    'maxCpu': 2,
    'maxMemory': 1024,
    'primaryIpAddress': '172.16.240.2',
    'globalIdentifier': '1a2b3c-1701',
    'primaryBackendIpAddress': '10.45.19.37',
    'hourlyBillingFlag': False,
}, {
    'id': 104,
    'hostname': 'cci-test2',
    'domain': 'test.sftlyr.ws',
    'fullyQualifiedDomainName': 'cci-test2.test.sftlyr.ws',
    'status': {'keyName': 'ACTIVE', 'name': 'Active'},
    # TODO - This needs to come from wherever data centers come from
    'datacenter': {'id': 50, 'name': 'TEST00',
                   'description': 'Test Data Center'},
    'powerState': {'keyName': 'RUNNING', 'name': 'Running'},
    'maxCpu': 4,
    'maxMemory': 4096,
    'primaryIpAddress': '172.16.240.7',
    'globalIdentifier': '05a8ac-6abf0',
    'primaryBackendIpAddress': '10.45.19.35',
    'hourlyBillingFlag': True,
}]

getMonthlyVirtualGuests = [cci for cci in getVirtualGuests
                           if not cci['hourlyBillingFlag']]
getHourlyVirtualGuests = [cci for cci in getVirtualGuests
                          if cci['hourlyBillingFlag']]


getHardware = [{
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
}, {
    'id': 1001,
    'datacenter': {'name': 'TEST00',
                   'description': 'Test Data Center'},
    'billingItem': {'id': 7112},
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
    ]
}]
getDomains = [{'name': 'example.com', 'id': 12345}]

getObject = {
    'networkVlans': [{
        'firewallNetworkComponents': [{'id': 1234}],
        'networkVlanFirewall': [{'id': 1234}],
        'dedicatedFirewallFlag': True,
        'firewallGuestNetworkComponents': [{'id': 1234}],
        'firewallInterfaces': [{'id': 1234}],
        'firewallRules': [{'id': 1234}],
        'highAvailabilityFirewallFlag': True,
    }]
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
    'privateResidenceFlag': 'privateResidenceFlag',
}

getGlobalIpRecords = [
    {
        'id': '200',
        'ipAddress': {
            'subnet': {
                'networkIdentifier': '10.0.0.1',
            },
        },
    }]

getSubnets = [
    {
        'id': '100',
        'networkIdentifier': '10.0.0.1',
        'datacenter': {'name': 'dal00'},
        'version': 4,
        'subnetType': 'PRIMARY'
    }]

getNetworkVlans = {'id': 1234}

getSshKeys = [{'id': '100', 'label': 'Test 1'},
              {'id': '101', 'label': 'Test 2', 'notes': 'Test notes'}]

getSecurityCertificates = [{'certificate': '1234',
                            'commonName': 'cert',
                            'id': 1234}]
getExpiredSecurityCertificates = getSecurityCertificates
getValidSecurityCertificates = getSecurityCertificates
