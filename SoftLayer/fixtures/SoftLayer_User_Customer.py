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
    'parent': {'id': 167758, 'username': 'SL12345'},
    'parentId': 167758,
    'postalCode': '77002',
    'pptpVpnAllowedFlag': False,
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

addBulkPortalPermission = True
removeBulkPortalPermission = True
createObject = getObject
editObject = True
addApiAuthenticationKey = True
