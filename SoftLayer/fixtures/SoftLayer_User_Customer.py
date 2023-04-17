getObject = {
    'accountId': 12345,
    'address1': '315 Test Street',
    'apiAuthenticationKeys': [{'authenticationKey': 'aaaaaaaaaaaaaaaaaaaaaaaaa'}],
    'city': 'Houston',
    'companyName': 'SoftLayer Development Community',
    'country': 'US',
    'createDate': '2014-08-18T12:58:02-06:00',
    'displayName': 'Test',
    'email': 'test@us.ibm.com',
    'firstName': 'Test',
    'id': 244956,
    'isMasterUserFlag': False,
    'lastName': 'Testerson',
    'openIdConnectUserName': 'test@us.ibm.com',
    'parent': {
        'id': 167758, 'username': 'SL12345'},
    'parentId': 167758,
    'postalCode': '77002',
    'sslVpnAllowedFlag': True,
    'state': 'TX',
    'statusDate': None,
    'successfulLogins': [
        {'createDate': '2018-05-08T15:28:32-06:00',
         'ipAddress': '175.125.126.118',
         'successFlag': True,
         'userId': 244956},
    ],
    'timezone': {
        'id': 113,
        'longName': '(GMT-06:00) America/Chicago - CST',
        'name': 'America/Chicago',
        'offset': '-0600',
        'shortName': 'CST'},
    'timezoneId': 113,
    'unsuccessfulLogins': [
        {'createDate': '2018-02-09T14:13:15-06:00',
         'ipAddress': '73.136.219.36',
         'successFlag': False,
         'userId': 244956},
    ],
    'userStatus': {'name': 'Active'},
    'userStatusId': 1001,
    'username': 'SL12345-test',
    'vpnManualConfig': False,
    'permissions': [
        {'key': 'ALL_1',
         'keyName': 'ACCESS_ALL_HARDWARE',
         'name': 'All Hardware Access'}
    ],
    'roles': []
}

getPermissions = [
    {'key': 'ALL_1',
     'keyName': 'ACCESS_ALL_HARDWARE',
     'name': 'All Hardware Access'},
    {'key': 'A_1',
     'keyName': 'ACCOUNT_SUMMARY_VIEW',
     'name': 'View Account Summary'},
    {'key': 'A_10',
     'keyName': 'ADD_SERVICE_STORAGE',
     'name': 'Add/Upgrade Storage (StorageLayer)'}
]

getLoginAttempts = [
    {
        "createDate": "2017-10-03T09:28:33-06:00",
        "ipAddress": "1.2.3.4",
        "successFlag": False,
        "userId": 1111,
        "username": "sl1234"
    }
]

getOverrides = [
    {
        'id': 3661234,
        'subnetId': 1234
    }
]

addBulkPortalPermission = True
removeBulkPortalPermission = True
createObject = getObject
editObject = True
addApiAuthenticationKey = True
updateVpnUser = True
removeDedicatedHostAccess = True
removeHardwareAccess = True
removeVirtualGuestAccess = True
addDedicatedHostAccess = True
addHardwareAccess = True
addVirtualGuestAccess = True
updateVpnPassword = True

getHardware = [{
        "domain": "testedit.com",
        "fullyQualifiedDomainName": "test.testedit.com",
        "hardwareStatusId": 5,
        "hostname": "test",
        "id": 1403539,
        "manufacturerSerialNumber": "J33H9TX",
        "notes": "My golang note",
        "provisionDate": "2020-04-27T16:10:56-06:00",
        "serialNumber": "SL01FJUI",
        "globalIdentifier": "81434794-af69-44d5-bb97-6b6f43454eee",
        "hardwareStatus": {
            "id": 5,
            "status": "ACTIVE"
        },
        "networkManagementIpAddress": "10.93.138.222",
        "primaryBackendIpAddress": "10.93.138.202",
        "primaryIpAddress": "169.48.191.244",
        "privateIpAddress": "10.93.138.202"
    }]
getDedicatedHosts = [
    {
        'createDate': '2021-11-18T15:13:57-06:00',
        'diskCapacity': 1200,
        'id': 656700,
        'memoryCapacity': 242,
        'modifyDate': '2022-04-26T10:49:48-06:00',
        'name': 'dedicatedhost01'
    },
    {
        'accountId': 307608,
        'cpuCount': 56,
        'createDate': '2022-02-18T12:47:30-06:00',
        'diskCapacity': 1200,
        'id': 691394,
        'memoryCapacity': 242,
        'modifyDate': '2022-04-18T11:24:20-06:00',
        'name': 'test'
    }
]
getVirtualGuests = [
    {
        "fullyQualifiedDomainName": "KVM-Test.cgallo.com",
        "hostname": "KVM-Test",
        "id": 121401696,
        "maxCpu": 2,
        "maxCpuUnits": "CORE",
        "maxMemory": 4096,
        "modifyDate": "2022-01-25T23:23:13-06:00",
        "provisionDate": "2021-06-09T14:51:54-06:00",
        "startCpus": 2,
        "typeId": 1,
        "uuid": "15951561-6171-0dfc-f3d2-be039e51cc10",
        "globalIdentifier": "a245a7dd-acd1-4d1a-9356-cc1ac6b55b98",
        "primaryBackendIpAddress": "10.208.73.53",
        "primaryIpAddress": "169.48.96.27",
    },
    {
        "createDate": "2020-11-16T09:01:57-06:00",
        "deviceStatusId": 8,
        "domain": "softlayer.test",
        "fullyQualifiedDomainName": "SuspendVsTest.softlayer.test",
        "hostname": "SuspendVsTest",
        "id": 112238162,
        "maxCpu": 8,
        "maxCpuUnits": "CORE",
        "maxMemory": 16384,
        "modifyDate": "2022-01-25T14:15:37-06:00",
        "provisionDate": "2020-11-16T09:09:04-06:00",
        "startCpus": 8,
        "typeId": 1,
        "uuid": "d8908a64-f4d4-5637-49c7-650572d47120",
        "globalIdentifier": "7fe777af-d38b-47c2-9f1c-b1ec26751b58",
        "primaryBackendIpAddress": "10.74.54.76",
    }]
