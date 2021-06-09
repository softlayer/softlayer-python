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
        "uniqueId": "9934111111111",
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
        "uniqueId": "9934111111111",
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
        "uniqueId": "424406419091111",
        "vendorName": "akamai",
        "header": "www.test.com",
        "httpPort": 83,
        "cname": "cdn.test.cloud",
        "originHost": "1.1.1.1",
        "cacheKeyQueryRule": "include: test"
    }
]
