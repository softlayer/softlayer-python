"""
    SoftLayer.tests.mocks.product_package_mock
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Mocks API calls documented at
    http://sldn.softlayer.com/reference/services/SoftLayer_Account

    :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
    :license: MIT, see LICENSE for more details.
"""
from mock import MagicMock


def getAllObjects_Mock():
    mock = MagicMock()

    mock.return_value = [
        {'id': 13, 'name': 'Mock Testing Package'},
        {'id': 27, 'name': 'An additional testing category'},
        {'id': 50, 'name': 'Bare Metal Instance'},
    ]

    return mock


def getCategories_Mock(bmc=False):
    if bmc:
        return get_bmc_categories_mock()
    else:
        return get_server_categories_mock()


def get_server_categories_mock():
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
                'packageId': 13,
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
                'packageId': 13
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
                'packageId': 13
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
                'packageId': 13,
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
                'packageId': 13,
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
                    'packageId': 13,
                    'title': 'CentOS',
                },
                {
                    'sort': 0,
                    'prices': debian_prices,
                    'itemCategoryId': 12,
                    'packageId': 13,
                    'title': 'Debian',
                },
                {
                    'sort': 0,
                    'prices': ubuntu_prices,
                    'itemCategoryId': 12,
                    'packageId': 13,
                    'title': 'Ubuntu',
                },
                {
                    'sort': 0,
                    'prices': windows_prices,
                    'itemCategoryId': 12,
                    'packageId': 13,
                    'title': 'Microsoft',
                },
                {
                    'sort': 10,
                    'prices': redhat_prices,
                    'itemCategoryId': 12,
                    'packageId': 13,
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
                    'packageId': 13,
                },
                {
                    'sort': 5,
                    'prices': dual_nic_prices,
                    'itemCategoryId': 26,
                    'packageId': 13,
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
                'packageId': 13}],
            'name': 'Disk Controller'
        },
    ]

    return mock


def get_bmc_categories_mock():
    mock = MagicMock()

    server_core_prices = [
        {
            'itemId': 1013,
            'setupFee': '0',
            'recurringFee': '159',
            'hourlyRecurringFee': '.5',
            'oneTimeFee': '0',
            'id': 1921,
            'sort': 0,
            'item': {
                'capacity': '2',
                'description': '2 x 2.0 GHz Core Bare Metal Instance - '
                '2 GB Ram',
                'id': 1013
            },
            'laborFee': '0',
        },
        {
            'itemId': 1014,
            'setupFee': '0',
            'recurringFee': '199',
            'hourlyRecurringFee': '.75',
            'oneTimeFee': '0',
            'id': 1922,
            'sort': 0,
            'item': {
                'capacity': '4',
                'description': '4 x 2.0 GHz Core Bare Metal Instance - '
                '4 GB Ram',
                'id': 1014
            },
            'laborFee': '0',
        }
    ]

    centos_prices = [
        {
            'itemId': 3921,
            'setupFee': '0',
            'recurringFee': '0',
            'hourlyRecurringFee': '0',
            'oneTimeFee': '0',
            'id': 13963,
            'sort': 0,
            'item': {
                'description': 'CentOS 6.0 - Minimal Install (64 bit)',
                'id': 3921
            },
            'laborFee': '0',
        },
        {
            'itemId': 3919,
            'setupFee': '0',
            'recurringFee': '0',
            'hourlyRecurringFee': '0',
            'oneTimeFee': '0',
            'id': 13961,
            'sort': 0,
            'item': {
                'description': 'CentOS 6.0 - LAMP Install (64 bit)',
                'id': 3919
            },
            'laborFee': '0',
        },
    ]

    redhat_prices = [
        {
            'itemId': 3838,
            'setupFee': '0',
            'recurringFee': '20',
            'laborFee': '0',
            'oneTimeFee': '0',
            'sort': 1,
            'item': {
                'description': 'Red Hat Enterprise Linux 6 - Minimal Install '
                '(64 bit)',
                'id': 3838
            },
            'id': 13798,
        },
        {
            'itemId': 3834,
            'setupFee': '0',
            'recurringFee': '20',
            'laborFee': '0',
            'oneTimeFee': '0',
            'sort': 1,
            'item': {
                'description': 'Red Hat Enterprise Linux 6 - LAMP Install '
                '(64 bit)',
                'id': 3834
            },
            'id': 13795,
        }
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
            'itemId': 4168,
            'setupFee': '0',
            'recurringFee': '0',
            'hourlyRecurringFee': '0',
            'oneTimeFee': '0',
            'id': 17434,
            'sort': 9,
            'item': {
                'description': 'Ubuntu Linux 12.04 LTS Precise Pangolin - '
                'LAMP Install (64 bit)',
                'id': 4168
            },
            'laborFee': '0',
        },
    ]

    windows_prices = [
        {
            'itemId': 936,
            'setupFee': '0',
            'recurringFee': '20',
            'hourlyRecurringFee': '.05',
            'oneTimeFee': '0',
            'id': 1752,
            'sort': 16,
            'item': {
                'description': 'Windows Server 2008 Standard Edition SP2 '
                '(64bit)',
                'id': 936
            },
            'laborFee': '0',
        },
        {
            'itemId': 938,
            'setupFee': '0',
            'recurringFee': '50',
            'hourlyRecurringFee': '.1',
            'oneTimeFee': '0',
            'id': 1761,
            'sort': 16,
            'item': {
                'description': 'Windows Server 2008 Enterprise Edition SP2 '
                '(64bit)',
                'id': 938
            },
            'laborFee': '0',
        },
        {
            'itemId': 940,
            'setupFee': '0',
            'recurringFee': '75',
            'hourlyRecurringFee': '.15',
            'oneTimeFee': '0',
            'id': 1770,
            'sort': 16,
            'item': {
                'description': 'Windows Server 2008 Datacenter Edition SP2 '
                '(64bit)',
                'id': 940
            },
            'laborFee': '0',
        },
        {
            'itemId': 4247,
            'setupFee': '0',
            'recurringFee': '75',
            'hourlyRecurringFee': '.15',
            'oneTimeFee': '0',
            'id': 21060,
            'sort': 17,
            'item': {
                'description': 'Windows Server 2012 Datacenter Edition With '
                'Hyper-V (64bit)',
                'id': 4247
            },
            'laborFee': '0',
        },
        {
            'itemId': 4248,
            'setupFee': '0',
            'recurringFee': '20',
            'hourlyRecurringFee': '.05',
            'oneTimeFee': '0',
            'id': 21074,
            'sort': 15,
            'item': {
                'description': 'Windows Server 2008 Standard SP1 with R2 '
                '(64 bit)',
                'id': 4248
            },
            'laborFee': '0',
        },
    ]

    disk_prices1 = [
        {
            'itemId': 14,
            'setupFee': '0',
            'recurringFee': '0',
            'hourlyRecurringFee': '0',
            'oneTimeFee': '0',
            'id': 1267,
            'sort': 0,
            'item': {
                'capacity': '500',
                'description': '500GB SATA II',
                'id': 14
            },
            'laborFee': '0',
        },
    ]

    disk_prices2 = [
        {
            'itemId': 13,
            'setupFee': '0',
            'recurringFee': '0',
            'hourlyRecurringFee': '0',
            'oneTimeFee': '0',
            'id': 19,
            'sort': 99,
            'item': {
                'capacity': '250',
                'description': '250GB SATA II',
                'id': 13
            },
            'laborFee': '0',
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
            'quantity': ''
        },
        {
            'itemId': 1284,
            'setupFee': '0',
            'recurringFee': '40',
            'hourlyRecurringFee': '.05',
            'oneTimeFee': '0',
            'id': 2314,
            'sort': 5,
            'item': {
                'capacity': '1000',
                'description': '1 Gbps Dual Public & Private Networks '
                '(up to 2 Gbps)',
                'id': 1284
            },
            'laborFee': '0',
        }
    ]

    mock.return_value = [
        {
            'categoryCode': 'server_core',
            'id': 110,
            'groups': [{
                'sort': 0,
                'prices': server_core_prices,
                'itemCategoryId': 110,
                'packageId': 50
            }],
            'name': 'Bare Metal Instance'
        },
        {
            'categoryCode': 'os',
            'id': 12,
            'groups': [
                {'sort': 0, 'prices': centos_prices, 'title': 'CentOS'},
                {'sort': 0, 'prices': redhat_prices, 'title': 'Redhat'},
                {'sort': 9, 'prices': ubuntu_prices, 'title': 'Ubuntu'},
                {'sort': 14, 'prices': windows_prices, 'title': 'Microsoft'}
            ],
            'name': 'Operating System'
        },
        {
            'categoryCode': 'disk0',
            'id': 4,
            'groups': [
                {
                    'sort': 0,
                    'prices': disk_prices1,
                    'itemCategoryId': 4,
                    'packageId': 50
                },
                {
                    'sort': 99,
                    'prices': disk_prices2,
                    'itemCategoryId': 4,
                    'packageId': 50
                }
            ],
            'name': 'First Hard Drive',
        },
        {
            'categoryCode': 'port_speed',
            'id': 26,
            'groups': [
                {
                    'sort': 0,
                    'prices': single_nic_prices,
                    'itemCategoryId': 26,
                    'packageId': 50
                },
                {
                    'sort': 5,
                    'prices': dual_nic_prices,
                    'itemCategoryId': 26,
                    'packageId': 50
                }
            ],
            'name': 'Uplink Port Speeds',
        },
    ]

    return mock


def getConfiguration_Mock(bmc=False):
    if bmc:
        return get_bmc_configuration_mock()
    else:
        return get_server_configuration_mock()


def get_bmc_configuration_mock():
    mock = MagicMock()
    mock.return_value = [
        {
            'sort': 1,
            'orderStepId': 1,
            'itemCategory': {
                'categoryCode': 'server_core',
                'name': 'Bare Metal Instance'
            },
            'isRequired': 0,
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
                'categoryCode': 'disk0',
                'name': 'First Hard Drive',
            },
            'sort': 0,
            'orderStepId': 1,
            'isRequired': 1,
        },
        {
            'itemCategory': {
                'categoryCode': 'port_speed',
                'name': 'Uplink Port Speeds'
            },
            'sort': 0,
            'orderStepId': 1,
            'isRequired': 1,
        },
    ]

    return mock


def get_server_configuration_mock():
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
