"""
    SoftLayer.tests.mocks.hardware_mock
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Mocks API calls documented at
    http://sldn.softlayer.com/reference/services/SoftLayer_Account

    :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
    :license: MIT, see LICENSE for more details.
"""
from mock import MagicMock


def getObject_Mock(hw_id):
    mock = MagicMock()

    return_values = get_raw_hardware_mocks()

    if hw_id in return_values:
        mock.return_value = return_values[hw_id]
    else:
        mock.return_value = {}

    return mock


def getReverseDomainRecords_Mock(hw_id):
    hardware = getObject_Mock(hw_id)

    mock = MagicMock()

    if hardware:
        hardware = hardware.return_value
        ip_parts = hardware['primaryBackendIpAddress'].split('.')
        ip_parts.reverse()
        reverse = '.'.join(ip_parts) + '.in-addr.arpa'
        mock.return_value = [{'resourceRecords': [{'data': reverse}]}]

    return mock


def get_raw_hardware_mocks():
    return {
        1000: {
            'id': 1000,
            # TODO - This needs to be moved to wherever data centers come from
            'datacenter': {'id': 50, 'name': 'TEST00',
                           'description': 'Test Data Center'},
            'billingItem': {'id': 6327, 'recurringFee': 1.54},
            'primaryIpAddress': '172.16.1.100',
            'hostname': 'hardware-test1',
            'domain': 'test.sftlyr.ws',
            'fullyQualifiedDomainName': 'hardware-test1.test.sftlyr.ws',
            'processorPhysicalCoreAmount': 2,
            'memoryCapacity': 2,
            'primaryBackendIpAddress': '10.1.0.2',
            'networkManagementIpAddress': '10.1.0.3',
            'hardwareStatus': {'status': 'ACTIVE'},
            'provisionDate': '2013-08-01 15:23:45',
            'notes': 'These are test notes.',
            'operatingSystem': {
                'softwareLicense': {
                    'softwareDescription': {
                        'referenceCode': 'Ubuntu',
                        'name': 'Ubuntu 12.04 LTS',
                    }
                },
                'passwords': [
                    {'username': 'root', 'password': 'abc123'}
                ],
            },
            'networkVlans': [
                {
                    'networkSpace': 'PRIVATE',
                    'vlanNumber': 1800,
                    'id': 9653
                },
                {
                    'networkSpace': 'PUBLIC',
                    'vlanNumber': 3672,
                    'id': 19082
                },
            ],
            'tagReferences': [
                {'tag': {'name': 'test_tag'}}
            ],
            'activeTransaction': {
                'transactionStatus': {
                    'name': 'TXN_NAME',
                    'friendlyName': 'Friendly Transaction Name',
                    'id': 6660
                }
            }
        },
        1001: {
            'id': 1001,
            # TODO - This needs to be moved to wherever data centers come from
            'datacenter': {'name': 'TEST00',
                           'description': 'Test Data Center'},
            'billingItem': {'id': 7112},
            'primaryIpAddress': '172.16.4.94',
            'hostname': 'hardware-test2',
            'domain': 'test.sftlyr.ws',
            'fullyQualifiedDomainName': 'hardware-test2.test.sftlyr.ws',
            'processorPhysicalCoreAmount': 4,
            'memoryCapacity': 4,
            'primaryBackendIpAddress': '10.1.0.3',
            'hardwareStatus': {'status': 'ACTIVE'},
            'provisionDate': '2013-08-03 07:15:22',
            'operatingSystem': {
                'softwareLicense': {
                    'softwareDescription': {
                        'referenceCode': 'Ubuntu',
                        'name': 'Ubuntu 12.04 LTS',
                    }
                }
            },
            'networkVlans': [
                {
                    'networkSpace': 'PRIVATE',
                    'vlanNumber': 1800,
                    'id': 9653
                },
                {
                    'networkSpace': 'PUBLIC',
                    'vlanNumber': 3672,
                    'id': 19082
                },
            ]
        },
    }
