getInvoiceTopLevelItems = [
    {
        "categoryCode": "sov_sec_ip_addresses_priv",
        "createDate": "2018-04-04T23:15:20-06:00",
        "description": "64 Portable Private IP Addresses",
        "id": 724951323,
        "oneTimeAfterTaxAmount": "0",
        "recurringAfterTaxAmount": "0",
        "hostName": "bleg",
        "domainName": "beh.com",
        "category": {"name": "Private (only) Secondary VLAN IP Addresses"},
        "children": [
            {
                "id": 12345,
                "category": {"name": "Fake Child Category"},
                "description": "Blah",
                "oneTimeAfterTaxAmount": 55.50,
                "recurringAfterTaxAmount": 0.10
            }
        ],
        "location": {"name": "fra02"}
    },
    {
        "categoryCode": "reserved_capacity",
        "createDate": "2024-07-03T22:08:36-07:00",
        "description": "B1.1x2 (1 Year Term) (721hrs * .025)",
        "id": 1111222,
        "oneTimeAfterTaxAmount": "0",
        "recurringAfterTaxAmount": "18.03",
        "category": {"name": "Reserved Capacity"},
        "children": [
            {
                "description": "1 x 2.0 GHz or higher Core",
                "id": 29819,
                "oneTimeAfterTaxAmount": "0",
                "recurringAfterTaxAmount": "10.00",
                "category": {"name": "Computing Instance"}
            },
            {
                "description": "2 GB",
                "id": 123456,
                "oneTimeAfterTaxAmount": "0",
                "recurringAfterTaxAmount": "2.33",
                "category": {"name": "RAM"}
            }
        ],
        "location": {"name": "dal10"}
    }
]
