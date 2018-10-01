verifyOrder = {
    'orderId': 1234,
    'orderDate': '2013-08-01 15:23:45',
    'prices': [{
        'id': 1,
        'laborFee': '2',
        'oneTimeFee': '2',
        'oneTimeFeeTax': '.1',
        'quantity': 1,
        'recurringFee': '2',
        'recurringFeeTax': '.1',
        'hourlyRecurringFee': '2',
        'setupFee': '1',
        'item': {'id': 1, 'description': 'this is a thing'},
    }]}
placeOrder = verifyOrder

# Reserved Capacity Stuff

rsc_verifyOrder = {
    'orderContainers': [
        {
            'locationObject': {
                'id': 1854895,
                'longName': 'Dallas 13',
                'name': 'dal13'
            },
            'name': 'test-capacity',
            'postTaxRecurring': '0.32',
            'prices': [
                {
                    'item': {
                        'id': 1,
                        'description': 'B1.1x2 (1 Year ''Term)',
                        'keyName': 'B1_1X2_1_YEAR_TERM',
                    }
                }
            ]
        }
    ],
    'postTaxRecurring': '0.32',
}

rsc_placeOrder = {
    'orderDate': '2013-08-01 15:23:45',
    'orderId': 1234,
    'orderDetails': {
        'postTaxRecurring': '0.32',
    },
    'placedOrder': {
        'status': 'Great, thanks for asking',
        'locationObject': {
            'id': 1854895,
            'longName': 'Dallas 13',
            'name': 'dal13'
        },
        'name': 'test-capacity',
        'items': [
            {
                'description': 'B1.1x2 (1 Year ''Term)',
                'keyName': 'B1_1X2_1_YEAR_TERM',
                'categoryCode': 'guest_core',
            }
        ]
    }
}

rsi_placeOrder = {
    'orderId': 1234,
    'orderDetails': {
        'prices': [
            {
                'id': 4,
                'item': {
                    'id': 1,
                    'description': 'B1.1x2 (1 Year ''Term)',
                    'keyName': 'B1_1X2_1_YEAR_TERM',
                }
            }
        ]
    }
}
