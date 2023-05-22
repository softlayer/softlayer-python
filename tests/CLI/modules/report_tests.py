"""
    SoftLayer.tests.CLI.modules.report_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
from SoftLayer import testing

import json
from unittest import mock as mock

from pprint import pprint as pp


class ReportTests(testing.TestCase):
    def test_bandwidth_summary_report(self):
        search_mock = self.set_mock('SoftLayer_Search', 'advancedSearch')
        search_mock.side_effect = [_bandwidth_advanced_search(), [], [], []]
        result = self.run_command(['report', 'bandwidth'])

        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Search', 'advancedSearch')
        json_output = json.loads(result.output)
        pp(json_output)
        self.assertEqual(5, len(json_output))
        self.assertEqual(100250634, json_output[0]['Id'])
        self.assertEqual('TestRegion', json_output[0]['Pool'])
        self.assertEqual('dal10', json_output[0]['Location'])
        self.assertEqual(['tag test', 'tag test2'], json_output[0]['Tags'])
        self.assertEqual('Virtual Private Rack', json_output[1]['Pool'])
        self.assertEqual('1.04 GB', json_output[2]['Total usage'])
        self.assertEqual('5.00 TB', json_output[2]['Allocation'])
        self.assertEqual('Unlimited', json_output[3]['Allocation'])
        self.assertEqual('Not Applicable', json_output[3]['Pool'])
        self.assertEqual('0.00 MB', json_output[3]['Data in'])
        self.assertEqual('0.00 MB', json_output[3]['Data out'])
        self.assertEqual('Pay-As-You-Go', json_output[4]['Allocation'])

    def test_dc_closure_report(self):
        search_mock = self.set_mock('SoftLayer_Search', 'advancedSearch')
        search_mock.side_effect = [_advanced_search(), [], [], []]
        result = self.run_command(['report', 'datacenter-closures'])

        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Network_Pod', 'getAllObjects', filter=mock.ANY, mask=mock.ANY)
        self.assert_called_with('SoftLayer_Search', 'advancedSearch')
        json_output = json.loads(result.output)
        pp(json_output)
        self.assertEqual(5, len(json_output))
        self.assertEqual('bcr01a.ams01', json_output[0]['POD'])


def _bandwidth_advanced_search():
    result = [
        {
            "matchedTerms": [],
            "relevanceScore": "1",
            "resource": {
                "fullyQualifiedDomainName": "test.com",
                "id": 100250634,
                "bandwidthAllocation": "250",
                "bandwidthAllotmentDetail": {
                    "id": 53306635,
                    "bandwidthAllotment": {
                        "bandwidthAllotmentTypeId": 2,
                        "id": 1289128,
                        "name": "TestRegion"
                    }
                },
                "billingItem": {
                    "createDate": "2022-03-07T05:28:44-06:00",
                    "id": 937460400,
                    "lastBillDate": "2023-05-03T23:07:54-06:00"
                },
                "datacenter": {
                    "id": 1441195,
                    "name": "dal10"
                },
                "inboundPublicBandwidthUsage": ".16204",
                "outboundPublicBandwidthUsage": ".01351",
                "primaryIpAddress": "169.46.48.110",
                "tagReferences": [
                    {
                        "id": 172236920,
                        "tag": {
                                    "id": 3414982,
                                    "name": "tag test"
                        }
                    },
                    {
                        "id": 172236918,
                        "tag": {
                            "id": 3307656,
                            "name": "tag test2"
                        }
                    }
                ]
            },
            "resourceType": "SoftLayer_Virtual_Guest"
        },
        {
            "matchedTerms": [],
            "relevanceScore": "1",
            "resource": {
                "fullyQualifiedDomainName": "test.cloud",
                "id": 1867001,
                "bandwidthAllocation": "20000",
                "bandwidthAllotmentDetail": {
                    "id": 37331756,
                    "bandwidthAllotment": {
                        "bandwidthAllotmentTypeId": 1,
                        "id": 138442,
                        "name": "Virtual Private Rack"
                    }
                },
                "billingItem": {
                    "createDate": "2020-04-27T14:02:03-06:00",
                    "id": 658642904,
                    "lastBillDate": "2023-05-03T23:07:47-06:00"
                },
                "datacenter": {
                    "id": 1441195,
                    "name": "dal10"
                },
                "inboundPublicBandwidthUsage": ".48562",
                "outboundPublicBandwidthUsage": ".1987",
                "primaryIpAddress": "169.48.191.246",
                "tagReferences": [
                    {
                        "id": 1060153378,
                        "tag": {
                                    "id": 4974546,
                                    "name": "tags"
                        }
                    }
                ]
            },
            "resourceType": "SoftLayer_Hardware"
        },
        {
            "matchedTerms": [],
            "relevanceScore": "1",
            "resource": {
                "fullyQualifiedDomainName": "testcommunity.cloud",
                "id": 3190740,
                "bandwidthAllocation": "5000",
                "bandwidthAllotmentDetail": {
                    "id": 50932574,
                    "bandwidthAllotment": {
                        "bandwidthAllotmentTypeId": 1,
                        "id": 138442,
                        "name": "Virtual Private Rack"
                    }
                },
                "billingItem": {
                    "createDate": "2022-08-11T11:39:55-06:00",
                    "id": 983649084,
                    "lastBillDate": "2023-05-03T23:07:48-06:00"
                },
                "datacenter": {
                    "id": 1441195,
                    "name": "dal10"
                },
                "inboundPublicBandwidthUsage": ".63179",
                "outboundPublicBandwidthUsage": ".40786",
                "primaryIpAddress": "52.118.38.243",
                "tagReferences": []
            },
            "resourceType": "SoftLayer_Hardware"
        },
        {
            "matchedTerms": [],
            "relevanceScore": "1",
            "resource": {
                "id": 47758,
                "name": "SLADC307608-jt48",
                        "billingItem": {
                            "createDate": "2022-02-11T09:49:16-06:00",
                            "id": 931026566,
                            "lastBillDate": "2023-05-03T23:08:02-06:00"
                        },
                "datacenter": {
                            "id": 2017603,
                            "name": "wdc07"
                        },
                "primaryIpAddress": "169.62.12.146",
                "tagReferences": []
            },
            "resourceType": "SoftLayer_Network_Application_Delivery_Controller"
        },
        {
            "matchedTerms": [],
            "relevanceScore": "1",
            "resource": {
                "fullyQualifiedDomainName": "lab-web.test.com",
                "id": 127890106,
                "bandwidthAllocation": "0",
                "bandwidthAllotmentDetail": {
                    "id": 48915580,
                    "bandwidthAllotment": {
                        "bandwidthAllotmentTypeId": 1,
                        "id": 138442,
                        "name": "Virtual Private Rack"
                    }
                },
                "billingItem": {
                    "createDate": "2022-02-08T08:33:14-06:00",
                    "id": 930164384,
                    "lastBillDate": "2023-05-03T23:07:56-06:00"
                },
                "datacenter": {
                    "id": 138124,
                    "name": "dal05"
                },
                "inboundPrivateBandwidthUsage": ".00002",
                "inboundPublicBandwidthUsage": ".19583",
                "outboundPrivateBandwidthUsage": ".00002",
                "outboundPublicBandwidthUsage": ".18446",
                "primaryIpAddress": "108.168.148.26",
                "tagReferences": []
            },
            "resourceType": "SoftLayer_Virtual_Guest"
        }
    ]
    return result


def _advanced_search():
    results = [{'matchedTerms': ['primaryRouter.hostname:|fcr01a.mex01|'],
                'relevanceScore': '5.4415264',
                'resource': {'fullyQualifiedName': 'mex01.fcr01.858',
               'hardware': [{'billingItem': {'cancellationDate': None},
                             'fullyQualifiedDomainName': 'testpooling2.ibmtest.com',
                             'id': 1676221},
                            {'billingItem': {'cancellationDate': '2022-03-03T23:59:59-06:00'},
                             'fullyQualifiedDomainName': 'testpooling.ibmtest.com',
                             'id': 1534033}],
               'id': 1133383,
               'name': 'Mex-BM-Public',
               'networkSpace': 'PUBLIC',
               'privateNetworkGateways': [],
               'publicNetworkGateways': [],
               'virtualGuests': [],
               'vlanNumber': 858},
        'resourceType': 'SoftLayer_Network_Vlan'},
        {'matchedTerms': ['primaryRouter.hostname:|fcr01a.mex01|'],
         'relevanceScore': '5.4415264',
         'resource': {'fullyQualifiedName': 'mex01.fcr01.1257',
                      'hardware': [],
                      'id': 2912280,
                      'networkSpace': 'PUBLIC',
                      'privateNetworkGateways': [],
                      'publicNetworkGateways': [],
                      'virtualGuests': [{'billingItem': {'cancellationDate': None},
                                        'fullyQualifiedDomainName': 'imageTest.ibmtest.com',
                                         'id': 127270182},
                                        {'billingItem': {'cancellationDate': None},
                                        'fullyQualifiedDomainName': 'test.deleteme.com',
                                         'id': 106291032},
                                        {'billingItem': {'cancellationDate': None},
                                         'fullyQualifiedDomainName': 'testslack.test.com',
                                         'id': 127889958}],
                      'vlanNumber': 1257},
         'resourceType': 'SoftLayer_Network_Vlan'},
        {'matchedTerms': ['primaryRouter.hostname:|bcr01a.mex01|'],
         'relevanceScore': '5.003179',
         'resource': {'fullyQualifiedName': 'mex01.bcr01.1472',
                      'hardware': [],
                      'id': 2912282,
                      'networkSpace': 'PRIVATE',
                      'privateNetworkGateways': [],
                      'publicNetworkGateways': [],
                      'virtualGuests': [{'billingItem': {'cancellationDate': None},
                                        'fullyQualifiedDomainName': 'imageTest.ibmtest.com',
                                         'id': 127270182},
                                        {'billingItem': {'cancellationDate': None},
                                        'fullyQualifiedDomainName': 'test.deleteme.com',
                                         'id': 106291032},
                                        {'billingItem': {'cancellationDate': None},
                                         'fullyQualifiedDomainName': 'testslack.test.com',
                                         'id': 127889958}],
                      'vlanNumber': 1472},
         'resourceType': 'SoftLayer_Network_Vlan'},
        {'matchedTerms': ['primaryRouter.hostname:|bcr01a.mex01|'],
         'relevanceScore': '4.9517627',
         'resource': {'fullyQualifiedName': 'mex01.bcr01.1664',
                      'hardware': [{'billingItem': {'cancellationDate': '2022-03-03T23:59:59-06:00'},
                                   'fullyQualifiedDomainName': 'testpooling.ibmtest.com',
                                    'id': 1534033},
                                   {'billingItem': {'cancellationDate': None},
                                   'fullyQualifiedDomainName': 'testpooling2.ibmtest.com',
                                    'id': 1676221}],
                      'id': 3111644,
                      'name': 'testmex',
                      'networkSpace': 'PRIVATE',
                      'privateNetworkGateways': [],
                      'publicNetworkGateways': [],
                      'virtualGuests': [],
                      'vlanNumber': 1664},
         'resourceType': 'SoftLayer_Network_Vlan'},
        {'matchedTerms': ['primaryRouter.hostname:|bcr01a.mex01|'],
         'relevanceScore': '4.9517627',
         'resource': {'fullyQualifiedName': 'mex01.bcr01.1414',
                      'hardware': [],
                      'id': 2933662,
                      'name': 'test-for-trunks',
                      'networkSpace': 'PRIVATE',
                      'privateNetworkGateways': [],
                      'publicNetworkGateways': [],
                      'virtualGuests': [],
                      'vlanNumber': 1414},
         'resourceType': 'SoftLayer_Network_Vlan'}]
    return results
