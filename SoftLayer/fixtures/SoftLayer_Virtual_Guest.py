getObject = {
    'id': 100,
    'hostname': 'vs-test1',
    'domain': 'test.sftlyr.ws',
    'fullyQualifiedDomainName': 'vs-test1.test.sftlyr.ws',
    'status': {'keyName': 'ACTIVE', 'name': 'Active'},
    'billingItem': {
        'id': 6327,
        'nextInvoiceTotalRecurringAmount': 1.54,
        'children': [
            {'nextInvoiceTotalRecurringAmount': 1},
            {'nextInvoiceTotalRecurringAmount': 1},
            {'nextInvoiceTotalRecurringAmount': 1},
            {'nextInvoiceTotalRecurringAmount': 1},
            {'nextInvoiceTotalRecurringAmount': 1},
        ],
        'package': {
            "id": 835,
            "keyName": "PUBLIC_CLOUD_SERVER"
        },
        'orderItem': {
            'order': {
                'userRecord': {
                    'username': 'chechu',
                }
            }
        }
    },
    'datacenter': {'id': 50, 'name': 'TEST00',
                   'description': 'Test Data Center'},
    'powerState': {'keyName': 'RUNNING', 'name': 'Running'},
    'maxCpu': 2,
    'maxMemory': 1024,
    'primaryIpAddress': '172.16.240.2',
    'globalIdentifier': '1a2b3c-1701',
    'primaryBackendIpAddress': '10.45.19.37',
    'primaryNetworkComponent': {'speed': 10, 'maxSpeed': 100},
    'hourlyBillingFlag': False,
    'createDate': '2013-08-01 15:23:45',
    'blockDevices': [{'device': 0, 'mountType': 'Disk', 'uuid': 1},
                     {'device': 1, 'mountType': 'Disk',
                      'diskImage': {'type': {'keyName': 'SWAP'}}},
                     {'device': 2, 'mountType': 'CD'},
                     {'device': 3, 'mountType': 'Disk', 'uuid': 3},
                     {'device': 4, 'mountType': 'Disk', 'uuid': 4,
                      'diskImage': {'metadataFlag': True}}],
    'notes': 'notes',
    'networkVlans': [{'networkSpace': 'PUBLIC',
                      'vlanNumber': 23,
                      'id': 1}],
    'dedicatedHost': {'id': 37401},
    'operatingSystem': {
        'passwords': [{'username': 'user', 'password': 'pass'}],
        'softwareLicense': {
            'softwareDescription': {'version': '12.04-64 Minimal for VSI',
                                    'name': 'Ubuntu'}}
    },
    'softwareComponents': [{
        'passwords': [{'username': 'user', 'password': 'pass'}],
        'softwareLicense': {
            'softwareDescription': {'name': 'Ubuntu'}}
    }],
    'tagReferences': [{'tag': {'name': 'production'}}],
}

getCreateObjectOptions = {
    'flavors': [
        {
            'flavor': {
                'keyName': 'B1_1X2X25'
            },
            'template': {
                'supplementalCreateObjectOptions': {
                    'flavorKeyName': 'B1_1X2X25'
                }
            }
        },
        {
            'flavor': {
                'keyName': 'B1_1X2X100'
            },
            'template': {
                'supplementalCreateObjectOptions': {
                    'flavorKeyName': 'B1_1X2X100'
                }
            }
        },
        {
            'flavor': {
                'keyName': 'BL1_1X2X100'
            },
            'template': {
                'supplementalCreateObjectOptions': {
                    'flavorKeyName': 'BL1_1X2X100'
                }
            }
        },
        {
            'flavor': {
                'keyName': 'BL2_1X2X100'
            },
            'template': {
                'supplementalCreateObjectOptions': {
                    'flavorKeyName': 'BL2_1X2X100'
                }
            }
        },
        {
            'flavor': {
                'keyName': 'C1_1X2X25'
            },
            'template': {
                'supplementalCreateObjectOptions': {
                    'flavorKeyName': 'C1_1X2X25'
                }
            }
        },
        {
            'flavor': {
                'keyName': 'M1_1X2X100'
            },
            'template': {
                'supplementalCreateObjectOptions': {
                    'flavorKeyName': 'M1_1X2X100'
                }
            }
        },
        {
            'flavor': {
                'keyName': 'AC1_1X2X100'
            },
            'template': {
                'supplementalCreateObjectOptions': {
                    'flavorKeyName': 'AC1_1X2X100'
                }
            }
        },
        {
            'flavor': {
                'keyName': 'ACL1_1X2X100'
            },
            'template': {
                'supplementalCreateObjectOptions': {
                    'flavorKeyName': 'ACL1_1X2X100'
                }
            }
        },
    ],
    'processors': [
        {
            'itemPrice': {
                'item': {'description': '1 x 2.0 GHz Core'},
                'hourlyRecurringFee': '.07',
                'recurringFee': '29'
            },
            'template': {'startCpus': 1}
        },
        {
            'itemPrice': {
                'item': {'description': '2 x 2.0 GHz Cores'},
                'hourlyRecurringFee': '.14',
                'recurringFee': '78'
            },
            'template': {'startCpus': 2}
        },
        {
            'itemPrice': {
                'item': {'description': '3 x 2.0 GHz Cores'},
                'hourlyRecurringFee': '.205',
                'recurringFee': '123.5'
            },
            'template': {'startCpus': 3}
        },
        {
            'itemPrice': {
                'item': {'description': '4 x 2.0 GHz Cores'},
                'hourlyRecurringFee': '.265',
                'recurringFee': '165.5'
            },
            'template': {'startCpus': 4}
        },
        {
            'itemPrice': {
                'hourlyRecurringFee': '.209',
                'recurringFee': '139',
                'dedicatedHostInstanceFlag': False,
                'item': {
                    'description': '1 x 2.0 GHz Cores (Dedicated)'
                }
            },
            'template': {
                'dedicatedAccountHostOnlyFlag': True,
                'startCpus': 1
            }
        },
        {
            'itemPrice': {
                'hourlyRecurringFee': '0',
                'recurringFee': '0',
                'dedicatedHostInstanceFlag': True,
                'item': {
                    'description': '56 x 2.0 GHz Cores (Dedicated Host)'
                }
            },
            'template': {
                'startCpus': 56,
                'dedicatedHost': {
                    'id': None
                }
            }
        },
        {
            'itemPrice': {
                'hourlyRecurringFee': '0',
                'recurringFee': '0',
                'dedicatedHostInstanceFlag': True,
                'item': {
                    'description': '4 x 2.0 GHz Cores (Dedicated Host)'
                }
            },
            'template': {
                'startCpus': 4,
                'dedicatedHost': {
                    'id': None
                }
            }
        },
    ],
    'memory': [
        {
            'itemPrice': {
                'item': {'description': '1 GB'},
                'hourlyRecurringFee': '.03',
                'recurringFee': '21'
            },
            'template': {'maxMemory': 1024}
        },
        {
            'itemPrice': {
                'item': {'description': '2 GB'},
                'hourlyRecurringFee': '.06',
                'recurringFee': '42'
            },
            'template': {'maxMemory': 2048}
        },
        {
            'itemPrice': {
                'item': {'description': '3 GB'},
                'hourlyRecurringFee': '.085',
                'recurringFee': '59.5'},
            'template': {'maxMemory': 3072}
        },
        {
            'itemPrice': {
                'item': {'description': '4 GB'},
                'hourlyRecurringFee': '.11',
                'recurringFee': '77'
            },
            'template': {'maxMemory': 4096}
        },
        {
            'itemPrice': {
                'hourlyRecurringFee': '0',
                'recurringFee': '0',
                'dedicatedHostInstanceFlag': True,
                'item': {
                    'description': '64 GB (Dedicated Host)'
                }
            },
            'template': {
                'maxMemory': 65536
            }
        },
        {
            'itemPrice': {
                'hourlyRecurringFee': '0',
                'recurringFee': '0',
                'dedicatedHostInstanceFlag': True,
                'item': {
                    'description': '8 GB (Dedicated Host)'
                }
            },
            'template': {
                'maxMemory': 8192
            }
        },
    ],
    'blockDevices': [
        {
            'itemPrice': {
                'item': {'description': '25 GB (LOCAL)'},
                'hourlyRecurringFee': '0',
                'recurringFee': '0'},
            'template': {
                'blockDevices': [
                    {'device': '0', 'diskImage': {'capacity': 25}}
                ],
                'localDiskFlag': True
            }
        },
        {
            'itemPrice': {
                'item': {'description': '100 GB (LOCAL)'},
                'hourlyRecurringFee': '.01',
                'recurringFee': '7'
            },
            'template': {
                'blockDevices': [
                    {'device': '0', 'diskImage': {'capacity': 100}}
                ],
                'localDiskFlag': True
            }
        },
    ],
    'operatingSystems': [
        {
            'itemPrice': {
                'item': {
                    'description': 'CentOS 6.0 - Minimal Install (64 bit)'
                },
                'hourlyRecurringFee': '0',
                'recurringFee': '0'
            },
            'template': {
                'operatingSystemReferenceCode': 'CENTOS_6_64'
            }
        },
        {
            'itemPrice': {
                'item': {
                    'description': 'Debian GNU/Linux 7.0 Wheezy/Stable -'
                                   ' Minimal Install (64 bit)'
                },
                'hourlyRecurringFee': '0',
                'recurringFee': '0'
            },
            'template': {
                'operatingSystemReferenceCode': 'DEBIAN_7_64'
            }
        },
        {
            'itemPrice': {
                'item': {
                    'description': 'Ubuntu Linux 12.04 LTS Precise'
                                   ' Pangolin - Minimal Install (64 bit)'
                },
                'hourlyRecurringFee': '0',
                'recurringFee': '0'
            },
            'template': {
                'operatingSystemReferenceCode': 'UBUNTU_12_64'
            }
        },
    ],
    'networkComponents': [
        {
            'itemPrice': {
                'item': {
                    'description': '10 Mbps Public & Private Networks'
                },
                'hourlyRecurringFee': '0',
                'recurringFee': '0'},
            'template': {
                'networkComponents': [{'maxSpeed': 10}]
            }
        },
        {
            'itemPrice': {
                'item': {'description': '100 Mbps Private Network'},
                'hourlyRecurringFee': '0',
                'recurringFee': '0'},
            'template': {
                'networkComponents': [{'maxSpeed': 100}]
            }
        },
        {
            'itemPrice': {
                'item': {'description': '1 Gbps Private Network'},
                'hourlyRecurringFee': '.02',
                'recurringFee': '10'
            },
            'template': {
                'networkComponents': [{'maxSpeed': 1000}]
            }
        },
        {
            'itemPrice': {
                'hourlyRecurringFee': '0',
                'recurringFee': '0',
                'dedicatedHostInstanceFlag': True,
                'item': {
                    'description': '1 Gbps Public & Private Network Uplinks (Dedicated Host)'
                }
            },
            'template': {
                'networkComponents': [
                    {
                        'maxSpeed': 1000
                    }
                ],
                'privateNetworkOnlyFlag': False
            }
        },
    ],
    'datacenters': [
        {'template': {'datacenter': {'name': 'ams01'}}},
        {'template': {'datacenter': {'name': 'dal05'}}},
    ],
}

getReverseDomainRecords = [{
    'networkAddress': '12.34.56.78',
    'name': '12.34.56.78.in-addr.arpa',
    'resourceRecords': [{'data': 'test.softlayer.com.', 'id': 987654}],
    'updateDate': '2013-09-11T14:36:57-07:00',
    'serial': 1234665663,
    'id': 123456,
}]

editObject = True
deleteObject = True
setPrivateNetworkInterfaceSpeed = True
setPublicNetworkInterfaceSpeed = True
createObject = getObject
createObjects = [getObject]
generateOrderTemplate = {
    "imageTemplateId": None,
    "location": "1854895",
    "packageId": 835,
    "presetId": 405,
    "prices": [
        {
            "hourlyRecurringFee": "0",
            "id": 45466,
            "recurringFee": "0",
            "item": {
                "description": "CentOS 7.x - Minimal Install (64 bit)"
            }
        },
        {
            "hourlyRecurringFee": "0",
            "id": 2202,
            "recurringFee": "0",
            "item": {
                "description": "25 GB (SAN)"
            }
        },
        {
            "hourlyRecurringFee": "0",
            "id": 905,
            "recurringFee": "0",
            "item": {
                "description": "Reboot / Remote Console"
            }
        },
        {
            "hourlyRecurringFee": ".02",
            "id": 899,
            "recurringFee": "10",
            "item": {
                "description": "1 Gbps Private Network Uplink"
            }
        },
        {
            "hourlyRecurringFee": "0",
            "id": 1800,
            "item": {
                "description": "0 GB Bandwidth Allotment"
            }
        },
        {
            "hourlyRecurringFee": "0",
            "id": 21,
            "recurringFee": "0",
            "item": {
                "description": "1 IP Address"
            }
        },
        {
            "hourlyRecurringFee": "0",
            "id": 55,
            "recurringFee": "0",
            "item": {
                "description": "Host Ping"
            }
        },
        {
            "hourlyRecurringFee": "0",
            "id": 57,
            "recurringFee": "0",
            "item": {
                "description": "Email and Ticket"
            }
        },
        {
            "hourlyRecurringFee": "0",
            "id": 58,
            "recurringFee": "0",
            "item": {
                "description": "Automated Notification"
            }
        },
        {
            "hourlyRecurringFee": "0",
            "id": 420,
            "recurringFee": "0",
            "item": {
                "description": "Unlimited SSL VPN Users & 1 PPTP VPN User per account"
            }
        },
        {
            "hourlyRecurringFee": "0",
            "id": 418,
            "recurringFee": "0",
            "item": {
                "description": "Nessus Vulnerability Assessment & Reporting"
            }
        }
    ],
    "quantity": 1,
    "sourceVirtualGuestId": None,
    "sshKeys": [],
    "useHourlyPricing": True,
    "virtualGuests": [
        {
            "domain": "test.local",
            "hostname": "test"
        }
    ],
    "complexType": "SoftLayer_Container_Product_Order_Virtual_Guest"
}

setUserMetadata = ['meta']
reloadOperatingSystem = 'OK'
setTags = True
createArchiveTransaction = {}
executeRescueLayer = True

getUpgradeItemPrices = [
    {
        'id': 1007,
        'categories': [{'id': 80,
                        'name': 'Computing Instance',
                        'categoryCode': 'guest_core'}],
        'item': {
            'capacity': '4',
            'units': 'PRIVATE_CORE',
            'description': 'Computing Instance (Dedicated)',
        }
    },
    {
        'id': 1144,
        'locationGroupId': None,
        'categories': [{'id': 80,
                        'name': 'Computing Instance',
                        'categoryCode': 'guest_core'}],
        'item': {
            'capacity': '4',
            'units': 'CORE',
            'description': 'Computing Instance',
        }
    },
    {
        'id': 332211,
        'locationGroupId': 1,
        'categories': [{'id': 80,
                        'name': 'Computing Instance',
                        'categoryCode': 'guest_core'}],
        'item': {
            'capacity': '4',
            'units': 'CORE',
            'description': 'Computing Instance',
        }
    },
    {
        'id': 1122,
        'categories': [{'id': 26,
                        'name': 'Uplink Port Speeds',
                        'categoryCode': 'port_speed'}],
        'item': {
            'capacity': '1000',
            'description': 'Public & Private Networks',
        }
    },
    {
        'id': 1144,
        'categories': [{'id': 26,
                        'name': 'Uplink Port Speeds',
                        'categoryCode': 'port_speed'}],
        'item': {
            'capacity': '1000',
            'description': 'Private Networks',
        }
    },
    {
        'id': 1133,
        'categories': [{'id': 3,
                        'name': 'RAM',
                        'categoryCode': 'ram'}],
        'item': {
            'capacity': '2',
            'description': 'RAM',
        }
    },
]

DEDICATED_GET_UPGRADE_ITEM_PRICES = [
    {
        'id': 115566,
        'categories': [{'id': 80,
                        'name': 'Computing Instance',
                        'categoryCode': 'guest_core'}],
        'item': {
            'capacity': '4',
            'units': 'DEDICATED_CORE',
            'description': 'Computing Instance (Dedicated Host)',
        }
    },
]
