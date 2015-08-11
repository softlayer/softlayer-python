createCancelServerTicket = {'id': 1234, 'title': 'Server Cancellation Request'}
getObject = {
    "guestNetworkComponentId": 1705294,
    "id": 1234,
    "status": "allow_edit",
    "billingItem": {
        "allowCancellationFlag": 1,
        "associatedBillingItemId": "20952512",
        "categoryCode": "firewall",
        "createDate": "2014-03-21T14:07:04-05:00",
        "cycleStartDate": "2014-03-21T14:07:04-05:00",
        "description": "10Mbps Hardware Firewall",
        "id": 21370814,
        "laborFee": "0",
        "laborFeeTaxRate": ".066",
        "lastBillDate": "2014-03-21T14:07:04-05:00",
        "modifyDate": "2014-03-21T14:07:07-05:00",
        "nextBillDate": "2014-04-04T00:00:00-05:00",
        "oneTimeFee": "0",
        "oneTimeFeeTaxRate": ".066",
        "orderItemId": 28712824,
        "parentId": 20952512,
        "recurringFee": "0",
        "recurringFeeTaxRate": ".066",
        "recurringMonths": 1,
        "serviceProviderId": 1,
        "setupFee": "0",
        "setupFeeTaxRate": ".066"
    },
    "guestNetworkComponent": {
        "createDate": "2014-03-17T13:49:00-05:00",
        "guestId": 3895386,
        "id": 1705294,
        "macAddress": "06:a4:8d:d2:88:34",
        "maxSpeed": 10,
        "modifyDate": "2014-03-17T13:49:20-05:00",
        "name": "eth",
        "networkId": 1310218,
        "port": 1,
        "speed": 10,
        "status": "ACTIVE",
        "uuid": "3f1b5e08-a652-fb3b-1baa-8ace70c90fe9",
        "guest": {
            "accountId": 307608,
            "dedicatedAccountHostOnlyFlag": False,
            "domain": "test.com",
            "fullyQualifiedDomainName": "test.test.com",
            "hostname": "firewalltest",
            "id": 3895386,
            "maxCpu": 1,
            "maxCpuUnits": "CORE",
            "maxMemory": 1024,
            "modifyDate": "2014-03-21T14:05:51-05:00",
            "startCpus": 1,
            "statusId": 1001,
            "uuid": "29b40ef0-a43a-8cb6-31be-1878cb6853f0",
            "status": {
                "keyName": "ACTIVE",
                "name": "Active"
            }
        }
    }
}

getRules = [
    {
        'destinationIpAddress': 'any on server',
        'protocol': 'tcp',
        'orderValue': 1,
        'destinationIpSubnetMask': '255.255.255.255',
        'destinationPortRangeStart': 80,
        'sourceIpSubnetMask': '0.0.0.0',
        'destinationPortRangeEnd': 80,
        'version': 4,
        'action': 'permit',
        'sourceIpAddress': '0.0.0.0'
    },
    {
        'destinationIpAddress': 'any on server',
        'protocol': 'tcp',
        'orderValue': 2,
        'destinationIpSubnetMask': '255.255.255.255',
        'destinationPortRangeStart': 1,
        'sourceIpSubnetMask': '255.255.255.255',
        'destinationPortRangeEnd': 65535,
        'version': 4,
        'action': 'permit',
        'sourceIpAddress': '193.212.1.10'
    },
    {
        'destinationIpAddress': 'any on server',
        'protocol': 'tcp',
        'orderValue': 3,
        'destinationIpSubnetMask': '255.255.255.255',
        'destinationPortRangeStart': 80,
        'sourceIpSubnetMask': '0.0.0.0',
        'destinationPortRangeEnd': 800,
        'version': 4,
        'action': 'permit',
        'sourceIpAddress': '0.0.0.0'
    }
]

getBillingItem = {"id": 21370814}
