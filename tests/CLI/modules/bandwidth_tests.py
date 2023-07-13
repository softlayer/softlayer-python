"""
    SoftLayer.tests.CLI.modules.bandwidth_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
from SoftLayer import testing

import json


class BandwidthTests(testing.TestCase):
    def test_bandwidth_pools(self):
        result = self.run_command(['bandwidth', 'pools'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Account', 'getBandwidthAllotments')
        self.assert_called_with('SoftLayer_Network_Bandwidth_Version1_Allotment', 'getObject')

    def test_acccount_bandwidth_pool_detail(self):
        result = self.run_command(['bandwidth', 'pools-detail', '123456'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Network_Bandwidth_Version1_Allotment', 'getObject')

    def test_bandwidth_summary(self):
        search_mock = self.set_mock('SoftLayer_Search', 'advancedSearch')
        search_mock.side_effect = [_bandwidth_advanced_search(), [], [], []]
        result = self.run_command(['bandwidth', 'summary'])

        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Search', 'advancedSearch')
        json_output = json.loads(result.output)
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

    def test_create_bandwidth(self):
        result = self.run_command(['bandwidth', 'pools-create', '--name=NewRegion', '--region=SJC/DAL/WDC/TOR/MON'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Network_Bandwidth_Version1_Allotment', 'createObject')
        json_output = json.loads(result.output)
        self.assertEqual(123456789, json_output['Id'])
        self.assertEqual('NewRegion', json_output['Name Pool'])
        self.assertEqual('SJC/DAL/WDC/TOR/MON', json_output['Region'])

    def test_edit_bandwidth(self):
        result = self.run_command(['bandwidth', 'pools-edit', '123456', '--name=MexRegionEdited'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Network_Bandwidth_Version1_Allotment', 'editObject')
        json_output = json.loads(result.output)
        self.assertEqual(123456, json_output['Id'])
        self.assertEqual('MexRegionEdited', json_output['Name Pool'])
        self.assertEqual('MEX', json_output['Region'])

    def test_delete_bandwidth(self):
        result = self.run_command(['bandwidth', 'pools-delete', '123456'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Network_Bandwidth_Version1_Allotment', 'requestVdrCancellation')
        json_output = json.loads(result.output)
        self.assertEqual("Bandwidth pool 123456 has been scheduled for deletion.", json_output)

    def test_create_bandwidth_single_region(self):
        result = self.run_command(['bandwidth', 'pools-create', '--name=NewRegion', '--region=AMS'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Network_Bandwidth_Version1_Allotment', 'createObject')
        json_output = json.loads(result.output)
        self.assertEqual(123456789, json_output['Id'])
        self.assertEqual('NewRegion', json_output['Name Pool'])
        self.assertEqual('AMS/LON/MAD/PAR', json_output['Region'])

    def test_bandwidth_pools_no_amount(self):
        bandwidth_mock = self.set_mock('SoftLayer_Account', 'getBandwidthAllotments')
        bandwidth_mock.return_value = [{
            'billingCyclePublicBandwidthUsage': {
                'amountIn': '6.94517'
                },
            'id': 309961,
            'locationGroup': {
                'description': 'All Datacenters in Mexico',
                'id': 262,
                'locationGroupTypeId': 1,
                'name': 'MEX',
                'securityLevelId': None
                },
            'billingItem': {'nextInvoiceTotalRecurringAmount': 0.0},
            'name': 'MexRegion',
            'projectedPublicBandwidthUsage': 9.88,
            'totalBandwidthAllocated': 3361
            }]
        result = self.run_command(['bandwidth', 'pools'])
        self.assert_no_fail(result)


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
