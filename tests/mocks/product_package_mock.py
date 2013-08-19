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

    centos_prices = [
        {
            'itemId': 3907,
            'setupFee': '0',
            'recurringFee': '0',
            'laborFee': '0',
            'oneTimeFee': '0',
            'sort': 0,
            'item': {
                'description': 'CentOS 6.0 (64 bit)',
                'id': 3907
            },
            'id': 13942,
        },
    ]

    debian_prices = [
        {
            'itemId': 3967,
            'setupFee': '0',
            'recurringFee': '0',
            'laborFee': '0',
            'oneTimeFee': '0',
            'sort': 6,
            'item': {
                'description': 'Debian GNU/Linux 6.0 Squeeze/Stable (32 bit)',
                'id': 3967
            },
            'id': 14046,
        },
    ]

    ubuntu_prices = [
        {
            'itemId': 4170,
            'setupFee': '0',
            'recurringFee': '0',
            'hourlyRecurringFee': '0',
            'oneTimeFee': '0',
            'id': 17438,
            'sort': 9,
            'item': {
                'description': 'Ubuntu Linux 12.04 LTS Precise Pangolin - '
                'Minimal Install (64 bit)',
                'id': 4170
            },
            'laborFee': '0',
        },
        {
            'itemId': 4166,
            'setupFee': '0',
            'recurringFee': '0',
            'laborFee': '0',
            'oneTimeFee': '0',
            'sort': 9,
            'item': {
                'description': 'Ubuntu Linux 12.04 LTS Precise Pangolin '
                '(64 bit)',
                'id': 4166
            },
            'id': 17430,
        },
    ]

    windows_prices = [
        {
            'itemId': 977,
            'setupFee': '0',
            'recurringFee': '40',
            'laborFee': '0',
            'oneTimeFee': '0',
            'sort': 15,
            'item': {
                'description': 'Windows Server 2008 R2 Standard Edition '
                '(64bit)',
                'id': 977
            },
            'id': 1858,
        },
        {
            'itemId': 978,
            'setupFee': '0',
            'recurringFee': '100',
            'laborFee': '0',
            'oneTimeFee': '0',
            'sort': 15,
            'item': {
                'description': 'Windows Server 2008 R2 Enterprise Edition '
                '(64bit)',
                'id': 978
            },
            'id': 1861,
        },
        {
            'itemId': 980,
            'setupFee': '0',
            'recurringFee': '150',
            'hourlyRecurringFee': '.21',
            'oneTimeFee': '0',
            'id': 1867,
            'sort': 15,
            'item': {
                'description': 'Windows Server 2008 R2 Datacenter Edition '
                'With Hyper-V (64bit)',
                'id': 980
            },
            'laborFee': '0',
        },
        {
            'itemId': 422,
            'setupFee': '0',
            'recurringFee': '40',
            'laborFee': '0',
            'oneTimeFee': '0',
            'sort': 18,
            'item': {
                'description': 'Windows Server 2003 Standard SP2 with R2 '
                '(64 bit)',
                'id': 422
            },
            'id': 692,
        },
    ]

    redhat_prices = [
        {
            'itemId': 3841,
            'setupFee': '0',
            'recurringFee': '0',
            'laborFee': '0',
            'oneTimeFee': '0',
            'sort': 10,
            'item': {
                'description': 'Red Hat Enterprise Linux - 6 (64 bit)',
                'id': 3841
            },
            'id': 13800,
        }
    ]

    ram_prices = [
        {
            'itemId': 254,
            'setupFee': '0',
            'recurringFee': '0',
            'laborFee': '0',
            'oneTimeFee': '0',
            'sort': 0,
            'item': {
                'capacity': '4',
                'description': '4 GB DIMM Registered 533/667',
                'id': 254
            },
            'id': 1023,
        },
        {
            'itemId': 255,
            'setupFee': '0',
            'recurringFee': '30',
            'laborFee': '0',
            'oneTimeFee': '0',
            'sort': 0,
            'item': {
                'capacity': '6',
                'description': '6 GB DIMM Registered 533/667',
                'id': 255
            },
            'id': 702,
        }]

    server_prices = [
        {
            'itemId': 300,
            'setupFee': '0',
            'recurringFee': '125',
            'laborFee': '0',
            'oneTimeFee': '0',
            'currentPriceFlag': '',
            'sort': 2,
            'item': {
                'description': 'Dual Quad Core Pancake 200 - 1.60GHz',
                'id': 300
            },
            'id': 723
        },
        {
            'itemId': 303,
            'setupFee': '0',
            'recurringFee': '279',
            'laborFee': '0',
            'oneTimeFee': '0',
            'currentPriceFlag': '',
            'sort': 2,
            'item': {
                'description': 'Dual Quad Core Pancake 200 - 1.80GHz',
                'id': 303
            },
            'id': 724,
        }
    ]

    single_nic_prices = [
        {
            'itemId': 187,
            'setupFee': '0',
            'recurringFee': '0',
            'hourlyRecurringFee': '0',
            'oneTimeFee': '0',
            'id': 273,
            'sort': 0,
            'item': {
                'capacity': '100',
                'description': '100 Mbps Public & Private Networks',
                'id': 187
            },
            'laborFee': '0',
        },
        {
            'itemId': 188,
            'setupFee': '0',
            'recurringFee': '20',
            'hourlyRecurringFee': '.04',
            'oneTimeFee': '0',
            'id': 274,
            'sort': 0,
            'item': {
                'capacity': '1000',
                'description': '1 Gbps Public & Private Networks',
                'id': 188
            },
            'laborFee': '0',
        }
    ]

    dual_nic_prices = [
        {
            'itemId': 4332,
            'setupFee': '0',
            'recurringFee': '10',
            'hourlyRecurringFee': '.02',
            'oneTimeFee': '0',
            'id': 21509,
            'sort': 5,
            'item': {
                'capacity': '10',
                'description': '10 Mbps Dual Public & Private Networks '
                '(up to 20 Mbps)',
                'id': 4332
            },
            'laborFee': '0',
        },
        {
            'itemId': 4336,
            'setupFee': '0',
            'recurringFee': '20',
            'hourlyRecurringFee': '.03',
            'oneTimeFee': '0',
            'id': 21513,
            'sort': 5,
            'item': {
                'capacity': '100',
                'description': '100 Mbps Dual Public & Private Networks '
                '(up to 200 Mbps)',
                'id': 4336
            },
            'laborFee': '0',
        }
    ]

    controller_prices = [
        {
            'itemId': 487,
            'setupFee': '0',
            'recurringFee': '0',
            'laborFee': '0',
            'oneTimeFee': '0',
            'sort': 0,
            'item': {
                'description': 'Non-RAID',
                'id': 487
            },
            'id': 876,
        },
        {
            'itemId': 488,
            'setupFee': '0',
            'recurringFee': '50',
            'laborFee': '0',
            'oneTimeFee': '0',
            'sort': 0,
            'item': {
                'description': 'RAID 0',
                'id': 488
            },
            'id': 877,
        }
    ]

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
            'categoryCode': 'ram',
            'id': 3,
            'name': 'Ram',
            'groups': [{
                'sort': 0,
                'prices': ram_prices,
                'itemCategoryId': 3,
                'packageId': 50
            }],
        },
        {
            'categoryCode': 'server',
            'id': 1,
            'name': 'Server',
            'groups': [{
                'sort': 2,
                'prices': server_prices,
                'itemCategoryId': 1,
                'packageId': 50
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
        },
        {
            'categoryCode': 'os',
            'id': 12,
            'name': 'Operating System',
            'groups': [
                {
                    'sort': 0,
                    'prices': centos_prices,
                    'itemCategoryId': 12,
                    'packageId': 50,
                    'title': 'CentOS',
                },
                {
                    'sort': 0,
                    'prices': debian_prices,
                    'itemCategoryId': 12,
                    'packageId': 50,
                    'title': 'Debian',
                },
                {
                    'sort': 0,
                    'prices': ubuntu_prices,
                    'itemCategoryId': 12,
                    'packageId': 50,
                    'title': 'Ubuntu',
                },
                {
                    'sort': 0,
                    'prices': windows_prices,
                    'itemCategoryId': 12,
                    'packageId': 50,
                    'title': 'Microsoft',
                },
                {
                    'sort': 10,
                    'prices': redhat_prices,
                    'itemCategoryId': 12,
                    'packageId': 50,
                    'title': 'Redhat'
                },
            ],
        },
        {
            'categoryCode': 'port_speed',
            'id': 26,
            'name': 'Uplink Port Speeds',
            'groups': [
                {
                    'sort': 0,
                    'prices': single_nic_prices,
                    'itemCategoryId': 26,
                    'packageId': 50,
                },
                {
                    'sort': 5,
                    'prices': dual_nic_prices,
                    'itemCategoryId': 26,
                    'packageId': 50,
                },
            ],
        },
        {
            'categoryCode': 'disk_controller',
            'id': 11,
            'groups': [{
                'sort': 0,
                'prices': controller_prices,
                'itemCategoryId': 11,
                'packageId': 50}],
            'name': 'Disk Controller'
        },
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
        },
        {
            'itemCategory': {
                'categoryCode': 'os',
                'name': 'Operating System',
            },
            'sort': 0,
            'orderStepId': 1,
            'isRequired': 1,
        },
        {
            'itemCategory': {
                'categoryCode': 'port_speed',
                'name': 'Uplink Port Speeds',
            },
            'sort': 2,
            'orderStepId': 1,
            'isRequired': 1,
        },
        {
            'itemCategory': {
                'categoryCode': 'ram',
                'name': 'RAM',
            },
            'sort': 2,
            'orderStepId': 1,
            'isRequired': 1,
        },
        {
            'itemCategory': {
                'categoryCode': 'disk_controller',
                'name': 'Disk Controller',
            },
            'sort': 2,
            'orderStepId': 1,
            'isRequired': 1,
        },
        {
            'itemCategory': {
                'categoryCode': 'server',
                'name': 'Server',
            },
            'sort': 2,
            'orderStepId': 1,
            'isRequired': 1,
        },
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
