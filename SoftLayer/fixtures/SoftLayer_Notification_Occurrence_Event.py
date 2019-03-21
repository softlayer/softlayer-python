getObject = {
    'endDate': '2019-03-18T17:00:00-06:00',
    'id': 1234,
    'lastImpactedUserCount': 417756,
    'modifyDate': '2019-03-12T15:32:48-06:00',
    'recoveryTime': None,
    'startDate': '2019-03-18T16:00:00-06:00',
    'subject': 'Public Website Maintenance',
    'summary': 'Blah Blah Blah',
    'systemTicketId': 76057381,
    'acknowledgedFlag': False,
    'attachments': [],
    'impactedResources': [{
        'resourceType': 'Server',
        'resourceTableId': 12345,
        'hostname': 'test',
        'privateIp': '10.0.0.1',
        'filterLable': 'Server'
    }],
    'notificationOccurrenceEventType': {'keyName': 'PLANNED'},
    'statusCode': {'keyName': 'PUBLISHED', 'name': 'Published'},
    'updates': [{
        'contents': 'More Blah Blah',
        'createDate': '2019-03-12T13:07:22-06:00',
        'endDate': None, 'startDate': '2019-03-12T13:07:22-06:00'
    }]
}

getAllObjects = [getObject]

acknowledgeNotification = True
