getObject = {
    'accountId': 1234,
    'id': 1234,
    'name': 'TestQuote1234',
    'quoteKey': '1234test4321',
    'order': {
        'id': 37623333,
        'items': [
            {
                'categoryCode': 'guest_core',
                'description': '4 x 2.0 GHz or higher Cores',
                'id': 468394713,
                'itemId': 859,
                'itemPriceId': '1642',
                'oneTimeAfterTaxAmount': '0',
                'oneTimeFee': '0',
                'oneTimeFeeTaxRate': '0',
                'oneTimeTaxAmount': '0',
                'quantity': 1,
                'recurringAfterTaxAmount': '0',
                'recurringFee': '0',
                'recurringTaxAmount': '0',
                'setupAfterTaxAmount': '0',
                'setupFee': '0',
                'setupFeeDeferralMonths': None,
                'setupFeeTaxRate': '0',
                'setupTaxAmount': '0',
                'package': {'id': 46, 'keyName': 'CLOUD_SERVER'}
            },
        ]
    }
}

getRecalculatedOrderContainer = {
    'presetId': '',
    'prices': [{
        'id': 1921
    }],
    'quantity': 1,
    'packageId': 50,
    'useHourlyPricing': '',
    'reservedCapacityId': '',

}

verifyOrder = {
    'orderId': 1234,
    'orderDate': '2013-08-01 15:23:45',
    'useHourlyPricing': False,
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
        'item': {'id': 1, 'description': 'this is a thing', 'keyName': 'TheThing'},
    }]}

placeOrder = {
    'orderId': 1234,
    'orderDate': '2013-08-01 15:23:45',
    'orderDetails': {
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
        }],
        'virtualGuests': [{
            'id': 1234567,
            'globalIdentifier': '1a2b3c-1701',
            'fullyQualifiedDomainName': 'test.guest.com'
        }],
    },
    'placedOrder': {
        'id': 37985543,
        'orderQuoteId': 2639077,
        'orderTypeId': 4,
        'status': 'PENDING_AUTO_APPROVAL',
        'items': [
            {
                'categoryCode': 'guest_core',
                'description': '4 x 2.0 GHz or higher Cores',
                'id': 472527133,
                'itemId': 859,
                'itemPriceId': '1642',
                'laborFee': '0',
                'oneTimeFee': '0',
                'recurringFee': '0',
                'setupFee': '0',
            }
        ]
    }
}

saveQuote = getObject
