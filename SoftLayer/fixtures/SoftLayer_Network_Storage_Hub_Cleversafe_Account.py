credentialCreate = {
    "accountId": "12345",
    "createDate": "2019-04-05T13:25:25-06:00",
    "id": 11111,
    "password": "nwUEUsx6PiEoN0B1Xe9z9hUCyXMkAFhDOjHqYJva",
    "username": "XfHhBNBPlPdlWyaPPJAI",
    "type": {
        "description": "A credential for generating S3 Compatible Signatures.",
        "keyName": "S3_COMPATIBLE_SIGNATURE",
        "name": "S3 Compatible Signature"
    }
}

getCredentials = [
    {
        "accountId": "12345",
        "createDate": "2019-04-05T13:25:25-06:00",
        "id": 11111,
        "password": "nwUEUsx6PiEoN0B1Xe9z9hUCyXMkAFhDOjHqYJva",
        "username": "XfHhBNBPlPdlWyaPPJAI",
        "type": {
            "description": "A credential for generating S3 Compatible Signatures.",
            "keyName": "S3_COMPATIBLE_SIGNATURE",
            "name": "S3 Compatible Signature"
        }
    },
    {
        "accountId": "12345",
        "createDate": "2019-04-05T13:25:25-06:00",
        "id": 11111,
        "password": "nwUEUsx6PiEoN0B1Xe9z9hUCyXMkAFhDOjHqYJva",
        "username": "XfHhBNBPlPdlWyaPPJAI",
        "type": {
            "description": "A credential for generating S3 Compatible Signatures.",
            "keyName": "S3_COMPATIBLE_SIGNATURE",
            "name": "S3 Compatible Signature"
        }
    }
]

getBuckets = [
    {
        "bytesUsed": 40540117,
        "name": "normal-bucket",
        "objectCount": 4,
        "storageLocation": "us-standard"
    }
]

getEndpoints = [
    {
        'legacy': False,
        'region': 'us-geo',
        'type': 'public',
        'url': 's3.us.cloud-object-storage.appdomain.cloud'
    },
    {
        'legacy': False,
        'region': 'us-geo',
        'type': 'private',
        'url': 's3.private.us.cloud-object-storage.appdomain.cloud'
    }
]
getCredentialLimit = 2

credentialDelete = True

getObject = {
    'id': 123456,
    'username': 'TEST307608-1',
    'credentials': [
        {
            'id': 1933496,
            'password': 'Um1Bp420FIFNvAg2QHjn5Sci2c2x4RNDXpVDDvnfsdsd1010',
            'username': 'Kv9aNIhtNa7ZRceabecs',
            'type': {
                'description': 'A credential for generating S3 Compatible Signatures.',
                'keyName': 'S3_COMPATIBLE_SIGNATURE'
            }
        },
        {

            'id': 1732820,
            'password': 'q6NtwqeuXDaRqGc0Jrugg2sDgbatyNsoN9sPEmjo',
            'username': '252r9BN8ibuDSQAXLOeL',
            'type': {
                'description': 'A credential for generating S3 Compatible Signatures.',
                'keyName': 'S3_COMPATIBLE_SIGNATURE',
            }
        }
    ],
    'uuid': '01c449c484ae4a58a42d9b79d4c5e4ed'
}
