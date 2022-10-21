getObject = {
    'id': 1234,
    'globalIdentifier': 'xxxxc-asd',
    'datacenter': {'id': 12, 'name': 'DALLAS21',
                   'description': 'Dallas 21'},
    'billingItem': {
        'id': 6327,
        'recurringFee': 1.54,
        'nextInvoiceTotalRecurringAmount': 16.08,
        'children': [
            {'description': 'test', 'nextInvoiceTotalRecurringAmount': 1},
        ],
        'orderItem': {
            'order': {
                'userRecord': {
                    'username': 'bob',
                }
            }
        }
    },
    'primaryIpAddress': '4.4.4.4',
    'hostname': 'testtest1',
    'domain': 'test.sftlyr.ws',
    'bareMetalInstanceFlag': True,
    'fullyQualifiedDomainName': 'testtest1.test.sftlyr.ws',
    'processorPhysicalCoreAmount': 4,
    'memoryCapacity': 4,
    'primaryBackendIpAddress': '10.4.4.4',
    'networkManagementIpAddress': '10.4.4.4',
    'hardwareStatus': {'status': 'ACTIVE'},
    'primaryNetworkComponent': {'maxSpeed': 1000, 'speed': 1000},
    'provisionDate': '2020-08-01 15:23:45',
    'notes': 'NOTES NOTES NOTES',
    'operatingSystem': {
        'softwareLicense': {
            'softwareDescription': {
                'referenceCode': 'UBUNTU_20_64',
                'name': 'Ubuntu',
                'version': 'Ubuntu 20.04 LTS',
            }
        },
        'passwords': [
            {'username': 'root', 'password': 'xxxxxxxxxxxx'}
        ],
    },
    'remoteManagementAccounts': [
        {'username': 'root', 'password': 'zzzzzzzzzzzzzz'}
    ],
    'networkVlans': [
        {
            'networkSpace': 'PRIVATE',
            'vlanNumber': 1234,
            'id': 11111
        },
    ],
    'tagReferences': [
        {'tag': {'name': 'a tag'}}
    ],
}

allowAccessToNetworkStorageList = True

getSensorData = [
    {
        "lowerCritical": "5.000",
        "lowerNonCritical": "10.000",
        "sensorId": "Ambient 1 Temperature",
        "sensorReading": "25.000",
        "sensorUnits": "degrees C",
        "status": "ok",
        "upperCritical": "43.000",
        "upperNonCritical": "41.000",
        "upperNonRecoverable": "46.000"
    },
    {
        "lowerCritical": "3500.000",
        "lowerNonCritical": "3700.000",
        "sensorId": "Fan 1 Tach",
        "sensorReading": "6580.000",
        "sensorUnits": "RPM",
        "status": "ok",
        "upperCritical": "25400.000",
        "upperNonCritical": "25300.000",
    }, {
        "sensorId": "IPMI Watchdog",
        "sensorReading": "0x0",
        "sensorUnits": "discrete",
        "status": "0x0080"
    }, {
        "sensorId": "Avg Power",
        "sensorReading": "70.000",
        "sensorUnits": "Watts",
        "status": "ok"
    },
    {
        "lowerCritical": "10.536",
        "lowerNonCritical": "10.780",
        "lowerNonRecoverable": "10.170",
        "sensorId": "12V",
        "sensorReading": "12.305",
        "sensorUnits": "Volts",
        "status": "ok",
        "upperCritical": "13.281",
        "upperNonCritical": "12.915",
        "upperNonRecoverable": "13.403"
    }]

getSoftwareComponents = [{
    "hardwareId": 123456,
    "id": 67064532,
    "passwords": [
        {
            "id": 77995567,
            "notes": "testslcli1",
            "password": "123456",
            "softwareId": 67064532,
            "username": "testslcli1",
        },
        {
            "id": 77944803,
            "notes": "testslcli2",
            "password": "test123",
            "softwareId": 67064532,
            "username": "testslcli2",
        }
    ],
    "softwareLicense": {
        "id": 21854,
        "softwareDescriptionId": 2914,
        "softwareDescription": {
            "id": 2914,
            "longDescription": "Ubuntu 20.04.1-64",
            "name": "Ubuntu",
            "referenceCode": "UBUNTU_20_64",
            "version": "20.04.1-64"
        }
    }
}]
