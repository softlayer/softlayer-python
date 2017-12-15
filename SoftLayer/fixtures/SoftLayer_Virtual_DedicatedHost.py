getObject = {
    'id': 37401,
    'memoryCapacity': 242,
    'modifyDate': '',
    'name': 'test-dedicated',
    'diskCapacity': 1200,
    'createDate': '2017-10-16T12:50:23-05:00',
    'cpuCount': 56,
    'accountId': 1199911
}


getAvailableRouters = [
    {'hostname': 'bcr01a.dal05', 'id': 51218},
    {'hostname': 'bcr02a.dal05', 'id': 83361},
    {'hostname': 'bcr03a.dal05', 'id': 122762},
    {'hostname': 'bcr04a.dal05', 'id': 147566}
]

getObjectById = {
    'datacenter': {
        'id': 138124,
        'name': 'dal05',
        'longName': 'Dallas 5'
    },
    'memoryCapacity': 242,
    'modifyDate': '2017-11-06T11:38:20-06:00',
    'name': 'khnguyendh',
    'diskCapacity': 1200,
    'backendRouter': {
        'domain': 'softlayer.com',
        'hostname': 'bcr01a.dal05',
        'id': 51218
    },
    'guestCount': 1,
    'cpuCount': 56,
    'guests': [{
        'domain': 'Softlayer.com',
        'hostname': 'khnguyenDHI',
        'id': 43546081,
        'uuid': '806a56ec-0383-4c2e-e6a9-7dc89c4b29a2'
    }],
    'billingItem': {
        'nextInvoiceTotalRecurringAmount': 1515.556,
        'orderItem': {
            'id': 263060473,
            'order': {
                'status': 'APPROVED',
                'privateCloudOrderFlag': False,
                'modifyDate': '2017-11-02T11:42:50-07:00',
                'orderQuoteId': '',
                'userRecordId': 6908745,
                'createDate': '2017-11-02T11:40:56-07:00',
                'impersonatingUserRecordId': '',
                'orderTypeId': 7,
                'presaleEventId': '',
                'userRecord': {
                    'username': '232298_khuong'
                },
                'id': 20093269,
                'accountId': 232298
            }
        },
        'id': 235379377,
        'children': [
            {
                'nextInvoiceTotalRecurringAmount': 0.0,
                'categoryCode': 'dedicated_host_ram'
            },
            {
                'nextInvoiceTotalRecurringAmount': 0.0,
                'categoryCode': 'dedicated_host_disk'
            }
        ]
    },
    'id': 44701,
    'createDate': '2017-11-02T11:40:56-07:00'
}
