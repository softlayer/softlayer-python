getObject = {
    "accountId": 12345,
    "createDate": "2014-03-18T15:26:55-07:00",
    "detailTypeId": 3,
    "id": 51990,
    "modifyDate": None,
    "regionalInternetRegistryHandleId": None,
    "properties": [
        {
            "createDate": "2014-03-18T15:26:55-07:00",
            "id": 85644,
            "modifyDate": "2020-11-12T16:21:57-06:00",
            "propertyType": {
                "createDate": None,
                "id": 2,
                "keyName": "FIRST_NAME",
                "modifyDate": None,
                "name": "FIRST_NAME",
                "valueExpression": ".*"
            },
            "propertyTypeId": 2,
            "registrationDetailId": 51990,
            "sequencePosition": 0,
            "value": "Boberson"
        }
    ]
}

editObjects = True
getProperties = [{
    'createDate': '2014-03-18T15:26:55-07:00',
    'id': 33333,
    'modifyDate': '2020-11-12T16:21:57-06:00',
    'propertyType': {
        'createDate': None,
        'id': 2,
        'keyName': 'FIRST_NAME',
        'modifyDate': None,
        'name': 'FIRST_NAME',
        'valueExpression': '.*'
    },
    'propertyTypeId': 2,
    'registrationDetailId': 12345,
    'sequencePosition': 0,
    'value': 'Boberson'
}]
getDetails = [{
    'createDate': '2015-05-27T17:24:25-07:00',
    'detailId': 12345,
    'id': 654321,
    'modifyDate': None,
    'registration': {
        'accountId': 1234,
        'cidr': 27,
        'createDate': '2015-05-27T17:24:25-07:00',
        'id': 10000,
        'modifyDate': '2015-05-27T17:26:59-07:00',
        'networkHandle': '159.122.23.224 - 159.122.23.255',
        'networkIdentifier': '159.122.23.224',
        'regionalInternetRegistryHandleId': 111111,
        'regionalInternetRegistryId': 4,
        'status': {
            'createDate': None,
            'id': 3,
            'keyName': 'REGISTRATION_COMPLETE',
            'modifyDate': None,
            'name': 'Registration Complete'
        },
        'statusId': 3
    },
    'registrationId': 222222
}]

createObject = getObject
