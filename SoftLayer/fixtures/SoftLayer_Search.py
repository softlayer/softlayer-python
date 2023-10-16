advancedSearch = [
    {
        "relevanceScore": "4",
        "resourceType": "SoftLayer_Hardware",
        "resource": {
            "accountId": 307608,
            "domain": "vmware.test.com",
            "fullyQualifiedDomainName": "host14.vmware.test.com",
            "hardwareStatusId": 5,
            "hostname": "host14",
            "id": 123456,
            "manufacturerSerialNumber": "AAAAAAAAA",
            "notes": "A test notes",
            "provisionDate": "2018-08-24T12:32:10-06:00",
            "serialNumber": "SL12345678",
            "serviceProviderId": 1,
            "hardwareStatus": {
                "id": 5,
                "status": "ACTIVE"
            }
        }
    }
]

search = advancedSearch

getObjectTypes = [{"name": "SoftLayer_Event_Log",
                   "properties": [
                       {
                           "name": "accountId",
                           "sortableFlag": True,
                           "type": "integer"
                       }]},
                  {"name": "SoftLayer_Hardware",
                   "properties": [
                       {
                           "name": "accountId",
                           "sortableFlag": True,
                           "type": "integer"
                       },
                       {
                           "name": "datacenter.longName",
                           "sortableFlag": True,
                           "type": "string"
                       },
                       {
                           "name": "deviceStatus.name",
                           "sortableFlag": True,
                           "type": "string"
                       }]
                   }]


advancedSearchVlan = [
    {
        "matchedTerms": [
            "name:|IBMPrivate|",
            "name.sort:|IBMPrivate|"
        ],
        "relevanceScore": "9.05",
        "resource": {
            "fullyQualifiedName": "dal10.bcr03.0000",
            "id": 11111,
            "name": "IBMPrivate",
            "vlanNumber": 0000,
            "networkSpace": "PRIVATE"
        },
        "resourceType": "SoftLayer_Network_Vlan"
    },
    {
        "matchedTerms": [
            "name:|IBMPublic|",
            "name.sort:|IBMPublic|"
        ],
        "relevanceScore": "9.01",
        "resource": {
            "fullyQualifiedName": "dal10.bcr03.11111",
            "id": 999999,
            "name": "IBMPublic",
            "vlanNumber": 11111,
            "networkSpace": "PUBLIC"
        },
        "resourceType": "SoftLayer_Network_Vlan"
    }
]
