from mock import MagicMock


def getAllObjects_Mock():
    mock = MagicMock()

    mock.return_value = [
        {'id': 13, 'name': 'Mock Testing Package'},
        {'id': 27, 'name': 'An additional testing category'},
        {'id': 50, 'name': 'Bare Metal Instance'},
    ]

    return mock


def getCategories_Mock():
    mock = MagicMock()

    prices = [{
        'itemId': 888,
        'id': 1888,
        'sort': 0,
        'setupFee': 0,
        'recurringFee': 0,
        'hourlyRecurringFee': 0,
        'oneTimeFee': 0,
        'laborFee': 0,
        'item': {
            'id': 888,
            'description': 'Some item',
            'capacity': 0,
        }
    }]

    disk0_prices = [{
        'itemId': 2000,
        'id': 12000,
        'sort': 0,
        'setupFee': 0,
        'recurringFee': 0,
        'hourlyRecurringFee': 0,
        'oneTimeFee': 0,
        'laborFee': 0,
        'item': {
            'id': 2000,
            'description': '1TB Drive',
            'capacity': 1000,
        }
    }]

    disk1_prices = [{
        'itemId': 2000,
        'id': 12000,
        'sort': 0,
        'setupFee': 0,
        'recurringFee': 25.0,
        'hourlyRecurringFee': 0,
        'oneTimeFee': 0,
        'laborFee': 0,
        'item': {
            'id': 2000,
            'description': '1TB Drive',
            'capacity': 1000,
        }
    }]

    category = _get_mock_category()
    mock.return_value = [
        {
            'categoryCode': category['categoryCode'],
            'name': category['name'],
            'id': 1000,
            'groups': [{
                'sort': 0,
                'prices': prices,
                'itemCategoryId': 1000,
                'packageId': 50,
            }],
        },
        {
            'categoryCode': 'disk0',
            'name': 'First Disk',
            'isRequired': 1,
            'id': 1001,
            'groups': [{
                'sort': 0,
                'prices': disk0_prices,
                'itemCategoryId': 1001,
                'packageId': 50,
            }],
        },
        {
            'categoryCode': 'disk1',
            'name': 'Second Disk',
            'isRequired': 1,
            'id': 1002,
            'groups': [{
                'sort': 0,
                'prices': disk1_prices,
                'itemCategoryId': 1002,
                'packageId': 50,
            }],
        }
    ]

    return mock


def getConfiguration_Mock():
    mock = MagicMock()
    mock.return_value = [
        {
            'itemCategory': _get_mock_category(),
            'sort': 0,
            'orderStepId': 1,
            'isRequired': 0,
        },
        {
            'itemCategory': {
                'categoryCode': 'disk0',
                'name': 'First Disk',
            },
            'sort': 0,
            'orderStepId': 1,
            'isRequired': 1,
        },
        {
            'itemCategory': {
                'categoryCode': 'disk1',
                'name': 'Second Disk',
            },
            'sort': 0,
            'orderStepId': 1,
            'isRequired': 1,
        }
    ]

    return mock


def getRegions_Mock():
    mock = MagicMock()

    mock.return_value = [{
        'location': {
            'locationPackageDetails': [{
                'deliveryTimeInformation': 'Typically 2-4 hours',
            }],
        },
        'keyname': 'RANDOM_LOCATION',
        'description': 'Random unit testing location',
    }]

    return mock


def _get_mock_category():
    # TODO - This might get moved into another mock module
    return {
        'categoryCode': 'random',
        'name': 'Random Category',
    }
