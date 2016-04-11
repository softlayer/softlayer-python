createCancelServerTicket = {'id': 1234, 'title': 'Server Cancellation Request'}
getObject = {
    "accountId": 1234,
    "assignedUserId": 12345,
    "createDate": "2013-08-01T14:14:04-07:00",
    "id": 100,
    "lastEditDate": "2013-08-01T14:16:47-07:00",
    "lastEditType": "AUTO",
    "modifyDate": "2013-08-01T14:16:47-07:00",
    "status": {
        "id": 1002,
        "name": "Closed"
    },
    "statusId": 1002,
    "title": "Cloud Instance Cancellation - 08/01/13",
    'updateCount': 3,
    'updates': [
        {'entry': 'a bot says something'},
        {'entry': 'user says something',
         'editor': {'firstName': 'John', 'lastName': 'Smith'}},
        {'entry': 'employee says something',
         'editor': {'displayName': 'emp1'}},

    ]
}

createStandardTicket = {
    "assignedUserId": 12345,
    "id": 100,
    "contents": "body",
    "subjectId": 1004,
    "title": "Cloud Instance Cancellation - 08/01/13"
}
edit = True
addUpdate = {}

addAttachedHardware = {
    "id": 123,
    "createDate": "2013-08-01T14:14:04-07:00",
    "hardwareId": 1,
    "ticketId": 100
}

addAttachedVirtualGuest = {
    "id": 123,
    "createDate": "2013-08-01T14:14:04-07:00",
    "virtualGuestId": 1,
    "ticketId": 100
}

removeAttachedHardware = True
removeAttachedVirtualGuest = True
