getObject = {
    'accountId': 1234,
    'id': 1234,
    'name': 'TestQuote1234',
    'quoteKey': '1234test4321',
}

getRecalculatedOrderContainer = {
    'orderContainers': [{
        'presetId': '',
        'prices': [{
            'id': 1921
        }],
        'quantity': 1,
        'packageId': 50,
        'useHourlyPricing': '',
    }],
}

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
