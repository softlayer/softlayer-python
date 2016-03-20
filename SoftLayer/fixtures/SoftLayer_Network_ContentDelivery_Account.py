getObject = {
    "cdnAccountName": "1234a",
    "providerPortalAccessFlag": False,
    "createDate": "2012-06-25T14:05:28-07:00",
    "id": 1234,
    "legacyCdnFlag": False,
    "dependantServiceFlag": True,
    "cdnSolutionName": "ORIGIN_PULL",
    "statusId": 4,
    "accountId": 1234,
    "status": {'name': 'ACTIVE'},
}

getOriginPullMappingInformation = [
    {
        "originUrl": "http://ams01.objectstorage.softlayer.net:80",
        "mediaType": "FLASH",
        "id": "12345",
        "isSecureContent": False
    },
    {
        "originUrl": "http://sng01.objectstorage.softlayer.net:80",
        "mediaType": "FLASH",
        "id": "12345",
        "isSecureContent": False
    }
]

createOriginPullMapping = True

deleteOriginPullRule = True

loadContent = True

purgeContent = True

purgeCache = True
