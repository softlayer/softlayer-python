listOriginPath = [
    {
        "header": "test.example.com",
        "httpPort": 80,
        "mappingUniqueId": "993419389425697",
        "origin": "10.10.10.1",
        "originType": "HOST_SERVER",
        "path": "/example",
        "status": "RUNNING"
    },
    {
        "header": "test.example.com",
        "httpPort": 80,
        "mappingUniqueId": "993419389425697",
        "origin": "10.10.10.1",
        "originType": "HOST_SERVER",
        "path": "/example1",
        "status": "RUNNING"
    }
]

createOriginPath = [
    {
        "httpPort": 80,
        "httpsPort": 81,
        "mappingUniqueId": "993419389425697",
        "origin": "10.10.10.1",
        "originType": "HOST_SERVER",
        "header": "test.example.com",
        "path": "/example",
        "status": "RUNNING",
        "bucketName": "test-bucket",
        'fileExtension': 'jpg',
        "performanceConfiguration": "Dynamic content acceleration",
        "dynamicContentAcceleration": {
                "detectionPath": "/abc.html",
                "prefetchEnabled": True,
                "mobileImageCompressionEnabled": True
            },
        "cacheKeyQueryRule": "include-all"
    }
]

deleteOriginPath = "Origin with path /example/videos/* has been deleted"
