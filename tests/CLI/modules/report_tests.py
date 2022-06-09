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

    def test_bandwidth_invalid_date(self):
        result = self.run_command(
            [
                'report',
                'bandwidth',
                '--start=welp',
                '--end=2016-01-01',
            ],
        )
        self.assertTrue('Invalid value for "--start"', result.output)

        result = self.run_command(
            [
                'report',
                'bandwidth',
                '--start=2016-01-01',
                '--end=welp',
            ],
        )
        self.assertTrue('Invalid value for "--end"', result.output)

    def test_bandwidth_report(self):
        racks = self.set_mock('SoftLayer_Account', 'getVirtualDedicatedRacks')
        racks.return_value = [{
            'id': 1,
            'name': 'pool1',
            'metricTrackingObjectId': 1,
        }, {
            'id': 2,
            'name': 'pool2',
        }, {
            'id': 3,
            'name': 'pool3',
            'metricTrackingObjectId': 3,
        }]
        hardware = self.set_mock('SoftLayer_Account', 'getHardware')
        hardware.return_value = [{
            'id': 101,
            'metricTrackingObject': {'id': 101},
            'hostname': 'host1',
        }, {
            'id': 102,
            'hostname': 'host2',
            'virtualRack': {'id': 1, 'bandwidthAllotmentTypeId': 2},
        }, {
            'id': 103,
            'metricTrackingObject': {'id': 103},
            'hostname': 'host3',
            'virtualRack': {'id': 1, 'bandwidthAllotmentTypeId': 2},
        }]
        guests = self.set_mock('SoftLayer_Account', 'getVirtualGuests')
        guests.return_value = [{
            'id': 201,
            'metricTrackingObjectId': 201,
            'hostname': 'host1',
        }, {
            'id': 202,
            'hostname': 'host2',
            'virtualRack': {'id': 2, 'bandwidthAllotmentTypeId': 2},
        }, {
            'id': 203,
            'metricTrackingObjectId': 203,
            'hostname': 'host3',
            'virtualRack': {'id': 2, 'bandwidthAllotmentTypeId': 2},
        }]
        summary_data = self.set_mock('SoftLayer_Metric_Tracking_Object', 'getSummaryData')
        summary_data.return_value = [
            {'type': 'publicIn_net_octet', 'counter': 10},
            {'type': 'publicOut_net_octet', 'counter': 20},
            {'type': 'privateIn_net_octet', 'counter': 30},
            {'type': 'privateOut_net_octet', 'counter': 40},
        ]

        result = self.run_command([
            'report',
            'bandwidth',
            '--start=2016-02-04',
            '--end=2016-03-04 12:34:56',
        ])

        self.assert_no_fail(result)

        stripped_output = '[' + result.output.split('[', 1)[1]
        json_output = json.loads(stripped_output)
        pp(json.loads(stripped_output))
        print("======= ^^^^^^^^^ ==============")
        self.assertEqual(json_output[0]['hostname'], 'pool1')
        self.assertEqual(json_output[0]['private_in'], 30)

        self.assertEqual(6, len(self.calls('SoftLayer_Metric_Tracking_Object', 'getSummaryData')))
        self.assert_called_with('SoftLayer_Metric_Tracking_Object', 'getSummaryData', identifier=1)
        self.assert_called_with('SoftLayer_Metric_Tracking_Object', 'getSummaryData', identifier=3)
        self.assert_called_with('SoftLayer_Metric_Tracking_Object', 'getSummaryData', identifier=101)
        self.assert_called_with('SoftLayer_Metric_Tracking_Object', 'getSummaryData', identifier=103)
        self.assert_called_with('SoftLayer_Metric_Tracking_Object', 'getSummaryData', identifier=201)
        self.assert_called_with('SoftLayer_Metric_Tracking_Object', 'getSummaryData', identifier=203)
        call = self.calls('SoftLayer_Metric_Tracking_Object', 'getSummaryData', identifier=1)[0]
        expected_args = ('2016-02-04 00:00:00 ', '2016-03-04 12:34:56 ',
                         [{
                             'keyName': 'PUBLICIN',
                             'name': 'publicIn',
                             'summaryType': 'sum',
                         }, {
                             'keyName': 'PUBLICOUT',
                             'name': 'publicOut',
                             'summaryType': 'sum',
                         }, {
                             'keyName': 'PRIVATEIN',
                             'name': 'privateIn',
                             'summaryType': 'sum',
                         }, {
                             'keyName': 'PRIVATEOUT',
                             'name': 'privateOut',
                             'summaryType': 'sum',
                         }],
                         300,
                         )
        self.assertEqual(expected_args, call.args)

    def test_virtual_bandwidth_report(self):
        racks = self.set_mock('SoftLayer_Account', 'getVirtualDedicatedRacks')
        racks.return_value = [{
            'id': 1,
            'name': 'pool1',
            'metricTrackingObjectId': 1,
        }, {
            'id': 2,
            'name': 'pool2',
        }, {
            'id': 3,
            'name': 'pool3',
            'metricTrackingObjectId': 3,
        }]
        guests = self.set_mock('SoftLayer_Account', 'getVirtualGuests')
        guests.return_value = [{
            'id': 201,
            'metricTrackingObjectId': 201,
            'hostname': 'host1',
        }, {
            'id': 202,
            'hostname': 'host2',
            'virtualRack': {'id': 2, 'bandwidthAllotmentTypeId': 2},
        }, {
            'id': 203,
            'metricTrackingObjectId': 203,
            'hostname': 'host3',
            'virtualRack': {'id': 2, 'bandwidthAllotmentTypeId': 2},
        }]
        summary_data = self.set_mock('SoftLayer_Metric_Tracking_Object',
                                     'getSummaryData')
        summary_data.return_value = [
            {'type': 'publicIn_net_octet', 'counter': 10},
            {'type': 'publicOut_net_octet', 'counter': 20},
            {'type': 'privateIn_net_octet', 'counter': 30},
            {'type': 'privateOut_net_octet', 'counter': 40},
        ]

        result = self.run_command([
            'report',
            'bandwidth',
            '--start=2016-02-04',
            '--end=2016-03-04 12:34:56',
            '--virtual',
        ])

        self.assert_no_fail(result)
        stripped_output = '[' + result.output.split('[', 1)[1]
        json_output = json.loads(stripped_output)
        self.assertEqual(json_output[0]['hostname'], 'pool1')
        self.assertEqual(json_output[1]['private_out'], 40)
        self.assertEqual(json_output[2]['private_in'], 30)
        self.assertEqual(json_output[3]['type'], 'virtual')

        self.assertEqual(4, len(self.calls('SoftLayer_Metric_Tracking_Object', 'getSummaryData')))
        self.assert_called_with('SoftLayer_Metric_Tracking_Object', 'getSummaryData', identifier=1)
        self.assert_called_with('SoftLayer_Metric_Tracking_Object', 'getSummaryData', identifier=3)
        self.assert_called_with('SoftLayer_Metric_Tracking_Object', 'getSummaryData', identifier=201)
        self.assert_called_with('SoftLayer_Metric_Tracking_Object', 'getSummaryData', identifier=203)
        call = self.calls('SoftLayer_Metric_Tracking_Object', 'getSummaryData', identifier=1)[0]
        expected_args = ('2016-02-04 00:00:00 ', '2016-03-04 12:34:56 ',
                         [{
                             'keyName': 'PUBLICIN',
                             'name': 'publicIn',
                             'summaryType': 'sum',
                         }, {
                             'keyName': 'PUBLICOUT',
                             'name': 'publicOut',
                             'summaryType': 'sum',
                         }, {
                             'keyName': 'PRIVATEIN',
                             'name': 'privateIn',
                             'summaryType': 'sum',
                         }, {
                             'keyName': 'PRIVATEOUT',
                             'name': 'privateOut',
                             'summaryType': 'sum',
                         }],
                         300,
                         )
        self.assertEqual(expected_args, call.args)

    def test_server_bandwidth_report(self):
        racks = self.set_mock('SoftLayer_Account', 'getVirtualDedicatedRacks')
        racks.return_value = [{
            'id': 1,
            'name': 'pool1',
            'metricTrackingObjectId': 1,
        }, {
            'id': 2,
            'name': 'pool2',
        }, {
            'id': 3,
            'name': 'pool3',
            'metricTrackingObjectId': 3,
        }]
        hardware = self.set_mock('SoftLayer_Account', 'getHardware')
        hardware.return_value = [{
            'id': 101,
            'metricTrackingObject': {'id': 101},
            'hostname': 'host1',
        }, {
            'id': 102,
            'hostname': 'host2',
            'virtualRack': {'id': 1, 'bandwidthAllotmentTypeId': 2},
        }, {
            'id': 103,
            'metricTrackingObject': {'id': 103},
            'hostname': 'host3',
            'virtualRack': {'id': 1, 'bandwidthAllotmentTypeId': 2},
        }]

        summary_data = self.set_mock('SoftLayer_Metric_Tracking_Object',
                                     'getSummaryData')
        summary_data.return_value = [
            {'type': 'publicIn_net_octet', 'counter': 10},
            {'type': 'publicOut_net_octet', 'counter': 20},
            {'type': 'privateIn_net_octet', 'counter': 30},
            {'type': 'privateOut_net_octet', 'counter': 40},
        ]

        result = self.run_command([
            'report',
            'bandwidth',
            '--start=2016-02-04',
            '--end=2016-03-04 12:34:56',
            '--server',
        ])

        self.assert_no_fail(result)
        stripped_output = '[' + result.output.split('[', 1)[1]
        json_output = json.loads(stripped_output)
        self.assertEqual(json_output[0]['hostname'], 'pool1')
        self.assertEqual(json_output[1]['private_out'], 40)
        self.assertEqual(json_output[2]['private_in'], 30)
        self.assertEqual(json_output[3]['type'], 'hardware')

        self.assertEqual(4, len(self.calls('SoftLayer_Metric_Tracking_Object', 'getSummaryData')))
        self.assert_called_with('SoftLayer_Metric_Tracking_Object', 'getSummaryData', identifier=101)
        self.assert_called_with('SoftLayer_Metric_Tracking_Object', 'getSummaryData', identifier=103)

        call = self.calls('SoftLayer_Metric_Tracking_Object', 'getSummaryData', identifier=1)[0]
        expected_args = ('2016-02-04 00:00:00 ', '2016-03-04 12:34:56 ',
                         [{
                             'keyName': 'PUBLICIN',
                             'name': 'publicIn',
                             'summaryType': 'sum',
                         }, {
                             'keyName': 'PUBLICOUT',
                             'name': 'publicOut',
                             'summaryType': 'sum',
                         }, {
                             'keyName': 'PRIVATEIN',
                             'name': 'privateIn',
                             'summaryType': 'sum',
                         }, {
                             'keyName': 'PRIVATEOUT',
                             'name': 'privateOut',
                             'summaryType': 'sum',
                         }],
                         300,
                         )
        self.assertEqual(expected_args, call.args)

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
