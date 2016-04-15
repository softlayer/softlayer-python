getObject = {
    'id': 100,
    'hostname': 'vs-test1',
    'domain': 'test.sftlyr.ws',
    'fullyQualifiedDomainName': 'vs-test1.test.sftlyr.ws',
    'status': {'keyName': 'ACTIVE', 'name': 'Active'},
    'billingItem': {
        'id': 6327,
        'recurringFee': 1.54,
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
    "primaryNetworkComponent": {"speed": 10, "maxSpeed": 100},
    'hourlyBillingFlag': False,
    'createDate': '2013-08-01 15:23:45',
    'blockDevices': [{"device": 0, 'mountType': 'Disk', "uuid": 1},
                     {"device": 1, 'mountType': 'Disk'},
                     {"device": 2, 'mountType': 'CD'},
                     {"device": 3, 'mountType': 'Disk', "uuid": 3}],
    'notes': 'notes',
    'networkVlans': [{'networkSpace': 'PUBLIC',
                      'vlanNumber': 23,
                      'id': 1}],
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
        }
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
generateOrderTemplate = {}
setUserMetadata = ['meta']
reloadOperatingSystem = 'OK'
setTags = True
createArchiveTransaction = {}
executeRescueLayer = True
