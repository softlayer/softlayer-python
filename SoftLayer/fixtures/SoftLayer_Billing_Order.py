getAllObjects = [{
    'accountId': 123456,
    'createDate': '2020-09-15T13:12:08-06:00',
    'id': 112356450,
    'modifyDate': '2020-09-15T13:13:13-06:00',
    'status': 'COMPLETED',
    'userRecordId': 987456321,
    'userRecord': {
        'username': 'test@test.com'
    },
    'items': [
        {
            'categoryCode': 'port_speed',
            'description': '100 Mbps Private Network Uplink'
        },
        {
            'categoryCode': 'service_port',
            'description': '100 Mbps Private Uplink'
        },
        {
            'categoryCode': 'public_port',
            'description': '0 Mbps Public Uplink'
        }
    ],
    'orderApprovalDate': '2020-09-15T13:13:13-06:00',
    'orderTotalAmount': '0'
},
    {
        'accountId': 123456,
        'createDate': '2019-09-15T13:12:08-06:00',
        'id': 645698550,
        'modifyDate': '2019-09-15T13:13:13-06:00',
        'status': 'COMPLETED',
        'userRecordId': 987456321,
        'userRecord': {
            'username': 'test@test.com'
        },
        'items': [
            {
                'categoryCode': 'port_speed',
                'description': '100 Mbps Private Network Uplink'
            },

        ],
        'orderApprovalDate': '2019-09-15T13:13:13-06:00',
        'orderTotalAmount': '0'
    }]

getObject = {
    'accountId': 1234,
    'createDate': '2020-09-23T16:22:30-06:00',
    'id': 6543210,
    'impersonatingUserRecordId': None,
    'initialInvoice': {
        'amount': '0',
        'id': 60012345,
        'invoiceTotalAmount': '0'
    },
    'items': [{
        'description': 'Dual Intel Xeon Silver 4210 (20 Cores, 2.20 GHz)'
    }],
    'modifyDate': '2020-09-23T16:22:32-06:00',
    'orderQuoteId': None,
    'orderTypeId': 11,
    'presaleEventId': None,
    'privateCloudOrderFlag': False,
    'status': 'APPROVED',
    'userRecord': {
        'displayName': 'testUser'
    },
    'userRecordId': 7654321,
}
