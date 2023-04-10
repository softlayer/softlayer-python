listDomainMappings = [
    {
        "cacheKeyQueryRule": "include-all",
        "cname": "cdnakauuiet7s6u6.cdnedge.bluemix.net",
        "createDate": "2020-09-29T15:19:01-06:00",
        "domain": "test.example.com",
        "header": "test.example.com",
        "httpPort": 80,
        "originHost": "1.1.1.1",
        "originType": "HOST_SERVER",
        "path": "/",
        "protocol": "HTTP",
        "status": "CNAME_CONFIGURATION",
        "uniqueId": "11223344",
        "vendorName": "akamai"
    }
]

listDomainMappingByUniqueId = [
    {
        "cname": "cdnakauuiet7s6u6.cdnedge.bluemix.net",
        "performanceConfiguration": "Large file optimization",
        "domain": "test.example.com",
        "header": "test.example.com",
        "httpPort": 80,
        "originHost": "1.1.1.1",
        "originType": "HOST_SERVER",
        "path": "/",
        "protocol": "HTTP",
        "status": "CNAME_CONFIGURATION",
        "uniqueId": "11223344",
        "vendorName": "akamai"
    }
]

updateDomainMapping = [
    {
        "createDate": "2021-02-09T19:32:29-06:00",
        "originType": "HOST_SERVER",
        "path": "/*",
        "performanceConfiguration": "Large file optimization",
        "protocol": "HTTP",
        "respectHeaders": True,
        "uniqueId": "11223344",
        "vendorName": "akamai",
        "header": "www.test.com",
        "httpPort": 83,
        "cname": "cdn.test.cloud",
        "originHost": "1.1.1.1",
        "cacheKeyQueryRule": "include: test"
    }
]

deleteDomainMapping = [
    {
        "akamaiCname": "wildcard.appdomain.mdc.edgekey.net",
        "certificateType": "NO_CERT",
        "cname": "cdnakayq9fye4t88239.cdn.appdomain.cloud",
        "createDate": "2023-03-29T07:33:42-06:00",
        "domain": "www.test.com",
        "header": "www.header.com",
        "httpPort": 80,
        "httpsPort": None,
        "modifyDate": "2023-03-29T07:33:46-06:00",
        "originHost": "67.228.227.82",
        "originType": "HOST_SERVER",
        "path": "/path/*",
        "performanceConfiguration": "General web delivery",
        "protocol": "HTTP",
        "respectHeaders": False,
        "serveStale": True,
        "status": "DELETING",
        "uniqueId": "303727924488685",
        "vendorName": "akamai"
    }
]
createDomainMapping = [
    {
        "bucketName": "test-bucket-name",
        "akamaiCname": "wildcard.appdomain.mdc.edgekey.net",
        "cacheKeyQueryRule": "include-all",
        "certificateType": "WILDCARD_CERT",
        "cname": "test.cdn.appdomain.cloud",
        "createDate": "2020-09-29T15:19:01-06:00",
        "domain": "test.com",
        "header": "header.test.com",
        "httpPort": 80,
        "httpsPort": None,
        "modifyDate": "2021-06-24T09:02:22-06:00",
        "originHost": "10.32.12.125",
        "originType": "HOST_SERVER",
        "path": "/*",
        "performanceConfiguration": "General web delivery",
        "protocol": "HTTP",
        "respectHeaders": True,
        "serveStale": True,
        "status": "CNAME_CONFIGURATION",
        "uniqueId": "354034879028850",
        "vendorName": "akamai"
    }
]
