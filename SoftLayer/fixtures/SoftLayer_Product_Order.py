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
        }]
    }
}

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

hardware_verifyOrder = {
    "currencyShortName": "USD",
    "hardware": [
        {
            "accountId": 1111,
            "domain": "testedit.com",
            "hostname": "test",
            "globalIdentifier": "81434794-af69-44d5-bb97-12312asdasdasd"
        }
    ],
    "location": "1441195",
    "locationObject": {
        "id": 1441195,
        "longName": "Dallas 10",
        "name": "dal10"
    },
    "packageId": 911,
    "postTaxRecurring": "0",
    "postTaxRecurringHourly": "0",
    "postTaxRecurringMonthly": "0",
    "preTaxRecurring": "0",
    "preTaxRecurringHourly": "0",
    "preTaxRecurringMonthly": "0",
    "prices": [
        {
            "hourlyRecurringFee": "0",
            "id": 209391,
            "recurringFee": "0",
            "categories": [
                {
                    "categoryCode": "ram",
                    "id": 3,
                    "name": "RAM"
                }
            ],
            "item": {
                "capacity": "32",
                "description": "32 GB RAM",
                "id": 11291,
                "units": "GB"
            }
        }
    ],
    "proratedInitialCharge": "0",
    "proratedOrderTotal": "0",
    "quantity": 1,
    "sendQuoteEmailFlag": None,
    "totalRecurringTax": "0",
    "useHourlyPricing": False
}

hardware_placeOrder = {
    "orderDate": "2021-05-07T07:41:41-06:00",
    "orderDetails": {
        "billingInformation": {
            "billingAddressLine1": "4849 Alpha Rd",
            "billingCity": "Dallas",
            "billingCountryCode": "US",
            "billingEmail": "test.ibm.com",
            "billingNameCompany": "SoftLayer Internal - Development Community",
            "billingNameFirst": "Test",
            "billingNameLast": "Test",
            "billingPhoneVoice": "1111111",
            "billingPostalCode": "75244-1111",
            "billingState": "TX",
        },
        "currencyShortName": "USD",
        "hardware": [
            {
                "accountId": 1111111,
                "bareMetalInstanceFlag": 0,
                "domain": "testedit.com",
                "fullyQualifiedDomainName": "test.testedit.com",
                "hostname": "test",
                "globalIdentifier": "81434794-af69-44d5-bb97-1111111"
            }
        ],
        "location": "1441195",
        "locationObject": {
            "id": 1441195,
            "longName": "Dallas 10",
            "name": "dal10"
        },
        "packageId": 911,
        "paymentType": "ADD_TO_BALANCE",
        "postTaxRecurring": "0",
        "postTaxRecurringHourly": "0",
        "postTaxRecurringMonthly": "0",
        "postTaxSetup": "0",
        "preTaxRecurring": "0",
        "preTaxRecurringHourly": "0",
        "preTaxRecurringMonthly": "0",
        "preTaxSetup": "0",
        "prices": [
            {
                "hourlyRecurringFee": "0",
                "id": 209391,
                "recurringFee": "0",
                "categories": [
                    {
                        "categoryCode": "ram",
                        "id": 3,
                        "name": "RAM"
                    }
                ],
                "item": {
                    "capacity": "32",
                    "description": "32 GB RAM",
                    "id": 11291,
                    "keyName": "RAM_32_GB_DDR4_2133_ECC_NON_REG",
                    "units": "GB",
                }
            }
        ],
        "proratedInitialCharge": "0",
        "proratedOrderTotal": "0",
        "quantity": 1,
        "totalRecurringTax": "0",
        "useHourlyPricing": False
    },
    "orderId": 78332111,
    "placedOrder": {
        "accountId": 1111111,
        "id": 1234,
        "status": "PENDING_UPGRADE",
        "account": {
            "brandId": 2,
            "companyName": "SoftLayer Internal - Development Community",
            "id": 1234
        },
        "items": [
            {
                "categoryCode": "ram",
                "description": "32 GB RAM",
                "id": 824199364,
                "recurringFee": "0"
            }
        ],
        "userRecord": {
            "accountId": 1234,
            "firstName": "test",
            "id": 3333,
            "lastName": "test",
            "username": "sl1234-test"
        }
    }
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
                },
                'hourlyRecurringFee': 1.0,
                'recurringFee': 2.0
            }
        ]
    }
}

wmware_placeOrder = {
    "orderDate": "2021-06-02 15:23:47",
    "orderId": 123456,
    "prices": [
        {
            "id": 176535,
            "itemId": 8109,
            "categories": [
                {
                    "categoryCode": "software_license",
                    "id": 438,
                    "name": "Software License"
                }
            ],
            "item": {
                "capacity": "1",
                "description": "VMware vSAN Advanced Tier III 64 - 124 TB 6.x",
                "id": 8109,
                "keyName": "VMWARE_VSAN_ADVANCE_TIER_III_64_124_6_X",
                "softwareDescription": {
                    "id": 1795,
                },
                "thirdPartyPolicyAssignments": [
                    {
                        "id": 29263,
                        "policyName": "3rd Party Software Terms VMWare v4"
                    }
                ]
            }
        }
    ]}

vlan_placeOrder = {"orderDate": "2021-06-02 15:23:47",
                   "orderId": 123456,
                   "orderDetails": {
                       "orderContainers": [{
                           "name": "test"}]},
                   "prices": [{
                       "id": 2018,
                       "itemId": 1071,
                       "categories": [{
                           "categoryCode": "network_vlan",
                           "id": 113,
                           "name": "Network Vlan"}],
                       "item": {
                           "capacity": "0",
                           "description": "Public Network Vlan",
                           "id": 1071,
                           "keyName": "PUBLIC_NETWORK_VLAN"}}
                   ]}
