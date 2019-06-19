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
        "header": "test.example.com",
        "httpPort": 80,
        "mappingUniqueId": "993419389425697",
        "origin": "10.10.10.1",
        "originType": "HOST_SERVER",
        "path": "/example",
        "status": "RUNNING",
        "bucketName": "test-bucket",
        'fileExtension': 'jpg',
        "performanceConfiguration": "General web delivery"
    }
]

deleteOriginPath = "Origin with path /example/videos/* has been deleted"
