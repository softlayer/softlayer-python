getObject = {
    "account": {
        "accountLinks": [
            {
                "accountId": 1472588,
                "createDate": "2019-06-10T16:19:47-06:00",
                "destinationAccountAlphanumericId": "84e014ba38fdsfg451659",
                "serviceProvider": {
                    "description": "Bluemix",
                    "id": 349,
                    "keyName": "BLUEMIX",
                    "name": "Bluemix"
                },
                "serviceProviderId": 349
            }
        ],
        "accountStatusId": 1001,
        "address1": "4567 street Rd",
        "allowedPptpVpnQuantity": 0,
        "brandId": 2,
        "city": "Dallas",
        "companyName": "test example company",
        "country": "US",
        "createDate": "2014-02-04T10:33:56-06:00",
        "email": "testExample@us.ibm.com",
        "firstName": "test",
        "id": 1472588,
        "isReseller": 0,
        "lastName": "Example",
        "modifyDate": "2014-02-04T10:34:18-06:00",
        "officePhone": "256325874579",
        "postalCode": "12369-852114",
        "resellerLevel": 0,
        "state": "TX",
    },
    "accountId": 1472588,
    "cidr": 31,
    "createDate": "2017-09-08T13:35:14-06:00",
    "id": 1536487,
    "modifyDate": "2020-03-17T12:05:36-06:00",
    "networkDetail": {
        "accountId": 1472588,
        "createDate": "2017-09-08T13:35:14-06:00",
        "detailType": {
            "id": 1,
            "keyName": "NETWORK",
            "name": "Network"
        },
        "detailTypeId": 1,
        "id": 1461143,
    },
    "networkIdentifier": "5.153.30.24",
    "personDetail": {
        "accountId": 1472588,
        "createDate": "2016-08-11T14:23:19-06:00",
        "detailType": {
            "id": 4,
            "keyName": "DEFAULT_PERSON",
            "name": "Default Person"
        },
        "detailTypeId": 4,
        "id": 971095,
    },
    "regionalInternetRegistryId": 4,
    "statusId": 5
}


createObject = getObject
editRegistrationAttachedDetails = True

getDetailReferences = [
    {
        "createDate": "2018-03-18T19:25:00-07:00",
        "detail": {
            "detailTypeId": 3,
            "id": 51990,
            "detailType": {
                "id": 3,
                "keyName": "PERSON",
                "name": "Person"
            }
        },
        "detailId": 51990,
        "id": 2971611,
        "modifyDate": "2020-12-03T15:33:05-06:00",
        "registration": {
            "accountId": 12345,
            "cidr": 29,
            "createDate": "2018-03-18T19:25:00-07:00",
            "id": 1731535,
            "modifyDate": "2020-12-03T15:33:12-06:00",
            "networkHandle": "169.46.48.104 - 169.46.48.111",
            "networkIdentifier": "169.46.48.104",
            "regionalInternetRegistryHandleId": 2020168,
            "regionalInternetRegistryId": 4,
            "statusId": 3,
        },
        "registrationId": 1731535
    },
    {
        "createDate": "2018-03-18T19:25:00-07:00",
        "detail": {
            "detailTypeId": 1,
            "id": 1672055,
            "detailType": {
                "id": 1,
                "keyName": "NETWORK",
                "name": "Network"
            }
        },
        "detailId": 1672055,
        "id": 2971613,
        "modifyDate": "",
        "registration": {
            "accountId": 12345,
            "cidr": 29,
            "createDate": "2018-03-18T19:25:00-07:00",
            "id": 1731535,
            "modifyDate": "2020-12-03T15:33:12-06:00",
            "networkHandle": "169.46.48.104 - 169.46.48.111",
            "networkIdentifier": "169.46.48.104",
            "regionalInternetRegistryHandleId": 2020168,
            "regionalInternetRegistryId": 4,
            "statusId": 3,
        },
        "registrationId": 1731535
    }
]

clearRegistration = True

createObjects = [getObject]
