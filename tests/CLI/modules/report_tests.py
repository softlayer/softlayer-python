"""
    SoftLayer.tests.CLI.modules.report_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
from SoftLayer import testing

import json


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
        ])

        self.assert_no_fail(result)
        stripped_output = '[' + result.output.split('[', 1)[1]
        self.assertEqual([
            {
                'hostname': 'pool1',
                'pool': None,
                'private_in': 30,
                'private_out': 40,
                'public_in': 10,
                'public_out': 20,
                'type': 'pool'
            }, {
                'hostname': 'pool3',
                'pool': None,
                'private_in': 30,
                'private_out': 40,
                'public_in': 10,
                'public_out': 20,
                'type': 'pool'
            }, {
                'hostname': 'host1',
                'pool': None,
                'private_in': 30,
                'private_out': 40,
                'public_in': 10,
                'public_out': 20,
                'type': 'hardware'
            }, {
                'hostname': 'host3',
                'pool': None,
                'private_in': 30,
                'private_out': 40,
                'public_in': 10,
                'public_out': 20,
                'type': 'hardware'
            }, {
                'hostname': 'host1',
                'pool': None,
                'private_in': 30,
                'private_out': 40,
                'public_in': 10,
                'public_out': 20,
                'type': 'virtual'
            }, {
                'hostname': 'host3',
                'pool': 2,
                'private_in': 30,
                'private_out': 40,
                'public_in': 10,
                'public_out': 20,
                'type': 'virtual'}],
            json.loads(stripped_output),
        )
        self.assertEqual(
            6,
            len(self.calls('SoftLayer_Metric_Tracking_Object',
                           'getSummaryData')),
        )
        self.assert_called_with('SoftLayer_Metric_Tracking_Object',
                                'getSummaryData',
                                identifier=1)
        self.assert_called_with('SoftLayer_Metric_Tracking_Object',
                                'getSummaryData',
                                identifier=3)
        self.assert_called_with('SoftLayer_Metric_Tracking_Object',
                                'getSummaryData',
                                identifier=101)
        self.assert_called_with('SoftLayer_Metric_Tracking_Object',
                                'getSummaryData',
                                identifier=103)
        self.assert_called_with('SoftLayer_Metric_Tracking_Object',
                                'getSummaryData',
                                identifier=201)
        self.assert_called_with('SoftLayer_Metric_Tracking_Object',
                                'getSummaryData',
                                identifier=203)
        call = self.calls('SoftLayer_Metric_Tracking_Object', 'getSummaryData',
                          identifier=1)[0]
        expected_args = (
            '2016-02-04 00:00:00 ',
            '2016-03-04 12:34:56 ',
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
        self.assertEqual([
            {
                'hostname': 'pool1',
                'pool': None,
                'private_in': 30,
                'private_out': 40,
                'public_in': 10,
                'public_out': 20,
                'type': 'pool',
            }, {
                'hostname': 'pool3',
                'pool': None,
                'private_in': 30,
                'private_out': 40,
                'public_in': 10,
                'public_out': 20,
                'type': 'pool',
            }, {
                'hostname': 'host1',
                'pool': None,
                'private_in': 30,
                'private_out': 40,
                'public_in': 10,
                'public_out': 20,
                'type': 'virtual',
            }, {
                'hostname': 'host3',
                'pool': 2,
                'private_in': 30,
                'private_out': 40,
                'public_in': 10,
                'public_out': 20,
                'type': 'virtual',
            }],
            json.loads(stripped_output),
        )
        self.assertEqual(
            4,
            len(self.calls('SoftLayer_Metric_Tracking_Object',
                           'getSummaryData')),
        )
        self.assert_called_with('SoftLayer_Metric_Tracking_Object',
                                'getSummaryData',
                                identifier=1)
        self.assert_called_with('SoftLayer_Metric_Tracking_Object',
                                'getSummaryData',
                                identifier=3)
        self.assert_called_with('SoftLayer_Metric_Tracking_Object',
                                'getSummaryData',
                                identifier=201)
        self.assert_called_with('SoftLayer_Metric_Tracking_Object',
                                'getSummaryData',
                                identifier=203)
        call = self.calls('SoftLayer_Metric_Tracking_Object', 'getSummaryData',
                          identifier=1)[0]
        expected_args = (
            '2016-02-04 00:00:00 ',
            '2016-03-04 12:34:56 ',
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
        self.assertEqual([
            {
                'hostname': 'pool1',
                'pool': None,
                'private_in': 30,
                'private_out': 40,
                'public_in': 10,
                'public_out': 20,
                'type': 'pool',
            }, {
                'hostname': 'pool3',
                'pool': None,
                'private_in': 30,
                'private_out': 40,
                'public_in': 10,
                'public_out': 20,
                'type': 'pool',
            }, {
                'hostname': 'host1',
                'pool': None,
                'private_in': 30,
                'private_out': 40,
                'public_in': 10,
                'public_out': 20,
                'type': 'hardware',
            }, {
                'hostname': 'host3',
                'pool': None,
                'private_in': 30,
                'private_out': 40,
                'public_in': 10,
                'public_out': 20,
                'type': 'hardware',
            }, ],
            json.loads(stripped_output),
        )
        self.assertEqual(
            4,
            len(self.calls('SoftLayer_Metric_Tracking_Object',
                           'getSummaryData')),
        )
        self.assert_called_with('SoftLayer_Metric_Tracking_Object',
                                'getSummaryData',
                                identifier=101)
        self.assert_called_with('SoftLayer_Metric_Tracking_Object',
                                'getSummaryData',
                                identifier=103)

        call = self.calls('SoftLayer_Metric_Tracking_Object', 'getSummaryData',
                          identifier=1)[0]
        expected_args = (
            '2016-02-04 00:00:00 ',
            '2016-03-04 12:34:56 ',
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
