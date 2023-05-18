"""
    SoftLayer.tests.CLI.modules.block_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
from SoftLayer.CLI import exceptions
from SoftLayer import SoftLayerAPIError
from SoftLayer import testing

import json
from unittest import mock as mock


class BlockTests(testing.TestCase):

    def test_access_list(self):
        result = self.run_command(['block', 'access-list', '1234'])

        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Network_Storage', 'getObject')

    def test_volume_cancel(self):
        result = self.run_command([
            '--really', 'block', 'volume-cancel', '1234'])

        self.assert_no_fail(result)
        self.assertEqual('Block volume with id 1234 has been marked'
                         ' for cancellation\n', result.output)
        self.assert_called_with('SoftLayer_Billing_Item', 'cancelItem',
                                args=(False, True, None))

    def test_volume_set_lun_id_in_range(self):
        lun_mock = self.set_mock('SoftLayer_Network_Storage', 'createOrUpdateLunId')
        lun_mock.return_value = dict(volumeId=1234, value='42')
        result = self.run_command('block volume-set-lun-id 1234 42'.split())
        self.assert_no_fail(result)
        self.assertEqual('Block volume with id 1234 is reporting LUN ID 42\n',
                         result.output)

    def test_volume_set_lun_id_in_range_missing_value(self):
        lun_mock = self.set_mock('SoftLayer_Network_Storage', 'createOrUpdateLunId')
        lun_mock.return_value = dict(volumeId=1234)
        result = self.run_command('block volume-set-lun-id 1234 42'.split())
        self.assert_no_fail(result)
        self.assertEqual('Failed to confirm the new LUN ID on volume 1234\n',
                         result.output)

    def test_volume_set_lun_id_not_in_range(self):
        value = '-1'
        lun_mock = self.set_mock('SoftLayer_Network_Storage', 'createOrUpdateLunId')
        lun_mock.side_effect = SoftLayerAPIError(
            'SoftLayer_Exception_Network_Storage_Iscsi_InvalidLunId',
            'The LUN ID specified is out of the valid range: %s [min: 0 max: 4095]' % (value))
        result = self.run_command('block volume-set-lun-id 1234 42'.split())
        self.assertIsNotNone(result.exception)
        self.assertIn('The LUN ID specified is out of the valid range', result.exception.faultString)

    def test_volume_detail(self):
        result = self.run_command(['block', 'volume-detail', '1234'])

        self.assert_no_fail(result)
        isinstance(json.loads(result.output)['IOPs'], float)
        self.assert_called_with('SoftLayer_Network_Storage', 'getObject', identifier=1234)
        self.assertEqual({
            'Username': 'username',
            'LUN Id': '2',
            'Notes': "{'status': 'available'}",
            'Endurance Tier': 'READHEAVY_TIER',
            'IOPs': 1000.0,
            'Snapshot Capacity (GB)': '10',
            'Snapshot Used (Bytes)': 1024,
            'Capacity (GB)': '20GB',
            'Target IP': '10.1.2.3',
            'Data Center': 'dal05',
            'Type': 'ENDURANCE',
            'ID': 100,
            '# of Active Transactions': '1',
            'Ongoing Transaction': 'This is a buffer time in which the customer may cancel the server',
            'Replicant Count': '1',
            'Replication Status': 'Replicant Volume Provisioning '
                                  'has completed.',
            'Replicant Volumes': [
                {'Name': 'Replicant Id', 'Value': 1785},
                {'Name': 'Volume Name', 'Value': 'TEST_REP_2'},
                {'Name': 'Target IP', 'Value': '10.3.177.84'},
                {'Name': 'Data Center', 'Value': 'dal01'},
                {'Name': 'Schedule', 'Value': 'REPLICATION_DAILY'}],
            'Original Volume Properties': [
                {'Property': 'Original Volume Size',
                 'Value': '20'},
                {'Property': 'Original Volume Name',
                 'Value': 'test-original-volume-name'},
                {'Property': 'Original Snapshot Name',
                 'Value': 'test-original-snapshot-name'}
            ]
        }, json.loads(result.output))

    def test_volume_detail_name_identifier(self):
        result = self.run_command(['block', 'volume-detail', 'SL-12345'])
        expected_filter = {
            'iscsiNetworkStorage': {
                'serviceResource': {
                    'type': {
                        'type': {'operation': '!~ ISCSI'}
                    }
                },
                'storageType': {
                    'keyName': {'operation': '*= BLOCK_STORAGE'}
                },
                'username': {'operation': '_= SL-12345'}
            }
        }

        self.assert_called_with('SoftLayer_Account', 'getIscsiNetworkStorage', filter=expected_filter)
        self.assert_called_with('SoftLayer_Network_Storage', 'getObject', identifier=100)
        self.assert_no_fail(result)

    def test_volume_list(self):
        result = self.run_command(['block', 'volume-list'])

        self.assert_no_fail(result)
        self.assertEqual([
            {
                'capacity_gb': 20,
                'datacenter': 'dal05',
                'id': 100,
                'IOPs': None,
                'ip_addr': '10.1.2.3',
                'lunId': None,
                'notes': "{'status': 'available'}",
                'rep_partner_count': None,
                'storage_type': 'ENDURANCE',
                'username': 'username',
                'active_transactions': None
            }],
            json.loads(result.output))

    @mock.patch('SoftLayer.BlockStorageManager.list_block_volumes')
    def test_volume_list_notes_format_output_json(self, list_mock):
        note_mock = 'test ' * 5
        list_mock.return_value = [
            {'notes': note_mock}
        ]

        result = self.run_command(['--format', 'json', 'block', 'volume-list', '--columns', 'notes'])

        self.assert_no_fail(result)
        self.assertEqual(
            [{
                'notes': note_mock,
            }],
            json.loads(result.output))

    @mock.patch('SoftLayer.BlockStorageManager.list_block_volumes')
    def test_volume_list_reduced_notes_format_output_table(self, list_mock):
        note_mock = 'test ' * 10
        expected_reduced_note = 'test ' * 4
        list_mock.return_value = [
            {'notes': note_mock}
        ]
        result = self.run_command(['--format', 'table', 'block', 'volume-list', '--columns', 'notes'])

        self.assert_no_fail(result)
        self.assertIn(expected_reduced_note, result.output)
        self.assertNotIn(note_mock, result.output)

    def test_volume_list_order(self):
        result = self.run_command(['block', 'volume-list', '--order=1234567'])

        self.assert_no_fail(result)
        json_result = json.loads(result.output)
        self.assertEqual(json_result[0]['id'], 100)

    @mock.patch('SoftLayer.BlockStorageManager.list_block_volumes')
    def test_volume_count(self, list_mock):
        list_mock.return_value = [
            {'serviceResource': {'datacenter': {'name': 'dal05'}}},
            {'serviceResource': {'datacenter': {'name': 'ams01'}}},
            {'serviceResource': {'datacenter': {'name': 'dal05'}}}
        ]

        result = self.run_command(['block', 'volume-count'])

        self.assert_no_fail(result)
        self.assertEqual(
            {
                'dal05': 2,
                'ams01': 1
            },
            json.loads(result.output))

    def test_volume_order_performance_iops_not_given(self):
        result = self.run_command(['block', 'volume-order',
                                   '--storage-type=performance', '--size=20',
                                   '--os-type=linux', '--location=dal05'])

        self.assertEqual(2, result.exit_code)

    def test_volume_order_performance_snapshot_error(self):
        result = self.run_command(['block', 'volume-order',
                                   '--storage-type=performance', '--size=20',
                                   '--iops=100', '--os-type=linux',
                                   '--location=dal05', '--snapshot-size=10',
                                   '--service-offering=performance'])

        self.assertEqual(2, result.exit_code)

    @mock.patch('SoftLayer.BlockStorageManager.order_block_volume')
    def test_volume_order_performance(self, order_mock):
        order_mock.return_value = {
            'placedOrder': {
                'id': 478,
                'items': [
                    {'description': 'Performance Storage'},
                    {'description': 'Block Storage'},
                    {'description': '0.25 IOPS per GB'},
                    {'description': '20 GB Storage Space'},
                    {'description': '10 GB Storage Space (Snapshot Space)'}]
            }
        }

        result = self.run_command(['block', 'volume-order',
                                   '--storage-type=performance', '--size=20',
                                   '--iops=100', '--os-type=linux',
                                   '--location=dal05', '--snapshot-size=10'])

        self.assert_no_fail(result)
        self.assertEqual(result.output,
                         'Order #478 placed successfully!\n'
                         ' > Performance Storage\n > Block Storage\n'
                         ' > 0.25 IOPS per GB\n > 20 GB Storage Space\n'
                         ' > 10 GB Storage Space (Snapshot Space)\n'
                         '\nYou may run "slcli block volume-list --order 478" to find this block volume '
                         'after it is ready.\n')

    def test_volume_order_endurance_tier_not_given(self):
        result = self.run_command(['block', 'volume-order',
                                   '--storage-type=endurance', '--size=20',
                                   '--os-type=linux', '--location=dal05'])

        self.assertEqual(2, result.exit_code)

    @mock.patch('SoftLayer.BlockStorageManager.order_block_volume')
    def test_volume_order_endurance(self, order_mock):
        order_mock.return_value = {
            'placedOrder': {
                'id': 478,
                'items': [
                    {'description': 'Endurance Storage'},
                    {'description': 'Block Storage'},
                    {'description': '0.25 IOPS per GB'},
                    {'description': '20 GB Storage Space'},
                    {'description': '10 GB Storage Space (Snapshot Space)'}]
            }
        }

        result = self.run_command(['block', 'volume-order',
                                   '--storage-type=endurance', '--size=20',
                                   '--tier=0.25', '--os-type=linux',
                                   '--location=dal05', '--snapshot-size=10'])

        self.assert_no_fail(result)
        self.assertEqual(result.output,
                         'Order #478 placed successfully!\n'
                         ' > Endurance Storage\n > Block Storage\n'
                         ' > 0.25 IOPS per GB\n > 20 GB Storage Space\n'
                         ' > 10 GB Storage Space (Snapshot Space)\n'
                         '\nYou may run "slcli block volume-list --order 478" to find this block volume '
                         'after it is ready.\n')

    @mock.patch('SoftLayer.BlockStorageManager.order_block_volume')
    def test_volume_order_order_not_placed(self, order_mock):
        order_mock.return_value = {}

        result = self.run_command(['block', 'volume-order',
                                   '--storage-type=endurance', '--size=20',
                                   '--tier=0.25', '--os-type=linux',
                                   '--location=dal05'])

        self.assert_no_fail(result)
        self.assertEqual(result.output,
                         'Order could not be placed! Please verify '
                         'your options and try again.\n')

    def test_volume_order_hourly_billing_not_available(self):
        result = self.run_command(['block', 'volume-order',
                                   '--storage-type=endurance', '--size=20',
                                   '--tier=0.25', '--os-type=linux',
                                   '--location=dal10', '--billing=hourly',
                                   '--service-offering=enterprise'])

        self.assertEqual(2, result.exit_code)

    @mock.patch('SoftLayer.BlockStorageManager.order_block_volume')
    def test_volume_order_hourly_billing(self, order_mock):
        order_mock.return_value = {
            'placedOrder': {
                'id': 10983647,
                'items': [
                    {'description': 'Storage as a Service'},
                    {'description': 'Block Storage'},
                    {'description': '20 GB Storage Space'},
                    {'description': '200 IOPS'}]
            }
        }

        result = self.run_command(['block', 'volume-order',
                                   '--storage-type=endurance', '--size=20',
                                   '--tier=0.25', '--os-type=linux',
                                   '--location=dal10', '--billing=hourly',
                                   '--service-offering=storage_as_a_service'])
        self.assert_no_fail(result)
        self.assertEqual(result.output,
                         'Order #10983647 placed successfully!\n'
                         ' > Storage as a Service\n'
                         ' > Block Storage\n'
                         ' > 20 GB Storage Space\n'
                         ' > 200 IOPS\n'
                         '\nYou may run "slcli block volume-list --order 10983647" to find this block volume '
                         'after it is ready.\n')

    @mock.patch('SoftLayer.BlockStorageManager.order_block_volume')
    def test_volume_order_performance_manager_error(self, order_mock):
        order_mock.side_effect = ValueError('failure!')

        result = self.run_command(['block', 'volume-order',
                                   '--storage-type=performance', '--size=20',
                                   '--iops=100', '--os-type=linux',
                                   '--location=dal05'])

        self.assertEqual(2, result.exit_code)
        self.assertEqual('Argument Error: failure!', result.exception.message)

    @mock.patch('SoftLayer.BlockStorageManager.order_block_volume')
    def test_volume_order_endurance_manager_error(self, order_mock):
        order_mock.side_effect = ValueError('failure!')

        result = self.run_command(['block', 'volume-order',
                                   '--storage-type=endurance', '--size=20',
                                   '--tier=0.25', '--os-type=linux',
                                   '--location=dal05'])

        self.assertEqual(2, result.exit_code)
        self.assertEqual('Argument Error: failure!', result.exception.message)

    def test_enable_snapshots(self):
        result = self.run_command(['block', 'snapshot-enable', '12345678',
                                   '--schedule-type=HOURLY', '--minute=10',
                                   '--retention-count=5'])

        self.assert_no_fail(result)

    def test_disable_snapshots(self):
        result = self.run_command(['block', 'snapshot-disable', '12345678',
                                   '--schedule-type=HOURLY'])
        self.assert_no_fail(result)

    def test_list_volume_schedules(self):
        result = self.run_command([
            'block', 'snapshot-schedule-list', '12345678'])
        self.assert_no_fail(result)
        self.assertEqual([
            {
                "week": None,
                "maximum_snapshots": None,
                "hour": None,
                "day_of_week": None,
                "day": None,
                "replication": None,
                "date_of_month": None,
                "month_of_year": None,
                "active": "",
                "date_created": "",
                "type": "WEEKLY",
                "id": 978,
                "minute": '30'
            },
            {
                "week": None,
                "maximum_snapshots": None,
                "hour": None,
                "day_of_week": None,
                "day": None,
                "replication": '*',
                "date_of_month": None,
                "month_of_year": None,
                "active": "",
                "date_created": "",
                "type": "INTERVAL",
                "id": 988,
                "minute": '*'
            }
        ], json.loads(result.output))

    def test_create_snapshot(self):
        result = self.run_command(['block', 'snapshot-create', '12345678'])

        self.assert_no_fail(result)

    @mock.patch('SoftLayer.BlockStorageManager.create_snapshot')
    def test_create_snapshot_unsuccessful(self, snapshot_mock):
        snapshot_mock.return_value = []

        result = self.run_command(['block', 'snapshot-create', '8', '-n=note'])

        self.assertEqual('Error occurred while creating snapshot.\n'
                         'Ensure volume is not failed over or in another '
                         'state which prevents taking snapshots.\n',
                         result.output)

    def test_snapshot_list(self):
        result = self.run_command(['block', 'snapshot-list', '12345678'])

        self.assert_no_fail(result)
        self.assertEqual([
            {
                'id': 470,
                'name': 'unit_testing_note',
                'created': '2016-07-06T07:41:19-05:00',
                'size_bytes': '42',
            }],
            json.loads(result.output))

    def test_snapshot_cancel(self):
        result = self.run_command(['--really',
                                   'block', 'snapshot-cancel', '1234'])

        self.assert_no_fail(result)
        self.assertEqual('Block volume with id 1234 has been marked'
                         ' for snapshot cancellation\n', result.output)
        self.assert_called_with('SoftLayer_Billing_Item', 'cancelItem',
                                args=(False, True, None))

    def test_snapshot_restore(self):
        result = self.run_command(['block', 'snapshot-restore', '12345678',
                                   '--snapshot-id=87654321'])

        self.assert_no_fail(result)
        self.assertEqual(result.output, 'Block volume 12345678 is being'
                         ' restored using snapshot 87654321\n')

    @mock.patch('SoftLayer.BlockStorageManager.order_snapshot_space')
    def test_snapshot_order_order_not_placed(self, order_mock):
        order_mock.return_value = {}

        result = self.run_command(['block', 'snapshot-order', '1234',
                                   '--size=10', '--tier=0.25', '--iops=100'])

        self.assert_no_fail(result)
        self.assertEqual(result.output,
                         'Order could not be placed! Please verify '
                         'your options and try again.\n')

    @mock.patch('SoftLayer.BlockStorageManager.order_snapshot_space')
    def test_snapshot_order_performance_manager_error(self, order_mock):
        order_mock.side_effect = ValueError('failure!')

        result = self.run_command(['block', 'snapshot-order', '1234',
                                   '--size=10', '--tier=0.25', '--iops=100'])

        self.assertEqual(2, result.exit_code)
        self.assertEqual('Argument Error: failure!', result.exception.message)

    @mock.patch('SoftLayer.BlockStorageManager.order_snapshot_space')
    def test_snapshot_order(self, order_mock):
        order_mock.return_value = {
            'placedOrder': {
                'id': 8702,
                'items': [{'description':
                           '10 GB Storage Space (Snapshot Space)'}],
                'status': 'PENDING_APPROVAL',
            }
        }

        result = self.run_command(['block', 'snapshot-order', '1234',
                                   '--size=10', '--tier=0.25', '--iops=100'])

        self.assert_no_fail(result)
        self.assertEqual(result.output,
                         'Order #8702 placed successfully!\n'
                         ' > 10 GB Storage Space (Snapshot Space)\n'
                         ' > Order status: PENDING_APPROVAL\n')

    def test_authorize_host_to_volume(self):
        result = self.run_command(['block', 'access-authorize', '12345678',
                                   '--hardware-id=100', '--virtual-id=10',
                                   '--ip-address-id=192',
                                   '--ip-address=192.3.2.1'])

        self.assert_no_fail(result)

    def test_deauthorize_host_to_volume(self):
        result = self.run_command(['block', 'access-revoke', '12345678',
                                   '--hardware-id=100', '--virtual-id=10',
                                   '--ip-address-id=192',
                                   '--ip-address=192.3.2.1'])

        self.assert_no_fail(result)

    def test_assign_subnets_to_acl(self):
        result = self.run_command(['block', 'subnets-assign', '12345',
                                   '--subnet-id=12345678'])

        self.assert_no_fail(result)

    def test_remove_subnets_from_acl(self):
        result = self.run_command(['block', 'subnets-remove', '12345',
                                   '--subnet-id=12345678'])

        self.assert_no_fail(result)

    def test_get_subnets_in_acl(self):
        result = self.run_command(['block', 'subnets-list', '12345'])

        self.assert_no_fail(result)

    def test_replicant_failover(self):
        result = self.run_command(['block', 'replica-failover', '12345678',
                                   '--replicant-id=5678'])

        self.assert_no_fail(result)
        self.assertEqual('Failover to replicant is now in progress.\n', result.output)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    @mock.patch('SoftLayer.BlockStorageManager.disaster_recovery_failover_to_replicant')
    def test_disaster_recovery_failover(self, disaster_recovery_failover_mock, confirm_mock):
        confirm_mock.return_value = True
        disaster_recovery_failover_mock.return_value = True
        result = self.run_command(['block', 'disaster-recovery-failover', '12345678',
                                   '--replicant-id=5678'])

        self.assert_no_fail(result)
        self.assertIn('Disaster Recovery Failover to replicant is now in progress.\n', result.output)

    def test_replication_locations(self):
        result = self.run_command(['block', 'replica-locations', '1234'])
        self.assert_no_fail(result)
        self.assertEqual(
            {
                '12345': 'Dallas 05',
            },
            json.loads(result.output))

    @mock.patch('SoftLayer.BlockStorageManager.get_replication_locations')
    def test_replication_locations_unsuccessful(self, locations_mock):
        locations_mock.return_value = False
        result = self.run_command(['block', 'replica-locations', '1234'])
        self.assert_no_fail(result)
        self.assertEqual('No data centers compatible for replication.\n',
                         result.output)

    def test_replication_partners(self):
        result = self.run_command(['block', 'replica-partners', '1234'])
        self.assert_no_fail(result)
        self.assertEqual([
            {
                'ID': 1784,
                'Account ID': 3000,
                'Capacity (GB)': 20,
                'Host ID': None,
                'Guest ID': None,
                'Hardware ID': None,
                'Username': 'TEST_REP_1',
            },
            {
                'ID': 1785,
                'Account ID': 3001,
                'Host ID': None,
                'Guest ID': None,
                'Hardware ID': None,
                'Capacity (GB)': 20,
                'Username': 'TEST_REP_2',
            }],
            json.loads(result.output))

    @mock.patch('SoftLayer.BlockStorageManager.get_replication_partners')
    def test_replication_partners_unsuccessful(self, partners_mock):
        partners_mock.return_value = False
        result = self.run_command(['block', 'replica-partners', '1234'])
        self.assertEqual(
            'There are no replication partners for the given volume.\n',
            result.output)

    @mock.patch('SoftLayer.BlockStorageManager.failover_to_replicant')
    def test_replicant_failover_unsuccessful(self, failover_mock):
        failover_mock.return_value = False

        result = self.run_command(['block', 'replica-failover', '12345678',
                                   '--replicant-id=5678'])

        self.assertEqual('Failover operation could not be initiated.\n',
                         result.output)

    @mock.patch('SoftLayer.CLI.formatting.confirm')
    def test_disaster_recovery_failover_aborted(self, confirm_mock):
        confirm_mock.return_value = False

        result = self.run_command(['block', 'disaster-recovery-failover', '12345678',
                                   '--replicant-id=5678'])

        self.assertEqual(result.exit_code, 2)
        self.assertIsInstance(result.exception, exceptions.CLIAbort)

    def test_replicant_failback(self):
        result = self.run_command(['block', 'replica-failback', '12345678'])

        self.assert_no_fail(result)
        self.assertEqual('Failback from replicant is now in progress.\n',
                         result.output)

    @mock.patch('SoftLayer.BlockStorageManager.failback_from_replicant')
    def test_replicant_failback_unsuccessful(self, failback_mock):
        failback_mock.return_value = False

        result = self.run_command(['block', 'replica-failback', '12345678'])

        self.assertEqual('Failback operation could not be initiated.\n',
                         result.output)

    @mock.patch('SoftLayer.BlockStorageManager.order_replicant_volume')
    def test_replicant_order_order_not_placed(self, order_mock):
        order_mock.return_value = {}

        result = self.run_command(['block', 'replica-order', '100',
                                   '--snapshot-schedule=DAILY',
                                   '--datacenter=dal05',
                                   '--iops=100'])

        self.assert_no_fail(result)
        self.assertEqual(result.output,
                         'Order could not be placed! Please verify '
                         'your options and try again.\n')

    @mock.patch('SoftLayer.BlockStorageManager.order_replicant_volume')
    def test_replicant_order(self, order_mock):
        order_mock.return_value = {
            'placedOrder': {
                'id': 91604,
                'items': [
                    {'description': 'Endurance Storage'},
                    {'description': '2 IOPS per GB'},
                    {'description': 'Block Storage'},
                    {'description': '20 GB Storage Space'},
                    {'description': '10 GB Storage Space (Snapshot Space)'},
                    {'description': '20 GB Storage Space Replicant of: TEST'},
                ],
            }
        }

        result = self.run_command(['block', 'replica-order', '100',
                                   '--snapshot-schedule=DAILY',
                                   '--datacenter=dal05', '--tier=2',
                                   '--iops=100'])

        self.assert_no_fail(result)
        self.assertEqual(result.output,
                         'Order #91604 placed successfully!\n'
                         ' > Endurance Storage\n'
                         ' > 2 IOPS per GB\n'
                         ' > Block Storage\n'
                         ' > 20 GB Storage Space\n'
                         ' > 10 GB Storage Space (Snapshot Space)\n'
                         ' > 20 GB Storage Space Replicant of: TEST\n')

    @mock.patch('SoftLayer.BlockStorageManager.order_duplicate_volume')
    def test_duplicate_order_exception_caught(self, order_mock):
        order_mock.side_effect = ValueError('order attempt failed, oh noooo!')

        result = self.run_command(['block', 'volume-duplicate', '102'])

        self.assertEqual(2, result.exit_code)
        self.assertEqual('Argument Error: order attempt failed, oh noooo!',
                         result.exception.message)

    @mock.patch('SoftLayer.BlockStorageManager.order_duplicate_volume')
    def test_duplicate_order_order_not_placed(self, order_mock):
        order_mock.return_value = {}

        result = self.run_command(['block', 'volume-duplicate', '102',
                                   '--duplicate-iops=1400'])

        self.assert_no_fail(result)
        self.assertEqual(result.output,
                         'Order could not be placed! Please verify '
                         'your options and try again.\n')

    @mock.patch('SoftLayer.BlockStorageManager.order_duplicate_volume')
    def test_duplicate_order(self, order_mock):
        order_mock.return_value = {
            'placedOrder': {
                'id': 24601,
                'items': [{'description': 'Storage as a Service'}]
            }
        }

        result = self.run_command(['block', 'volume-duplicate', '102',
                                   '--origin-snapshot-id=470',
                                   '--duplicate-size=250',
                                   '--duplicate-tier=2',
                                   '--duplicate-snapshot-size=20'])

        self.assert_no_fail(result)
        self.assertEqual(result.output,
                         'Order #24601 placed successfully!\n'
                         ' > Storage as a Service\n')

    @mock.patch('SoftLayer.BlockStorageManager.order_duplicate_volume')
    def test_duplicate_order_hourly_billing(self, order_mock):
        order_mock.return_value = {
            'placedOrder': {
                'id': 24602,
                'items': [{'description': 'Storage as a Service'}]
            }
        }

        result = self.run_command(['block', 'volume-duplicate', '100',
                                   '--origin-snapshot-id=470',
                                   '--duplicate-size=250',
                                   '--duplicate-tier=2', '--billing=hourly',
                                   '--duplicate-snapshot-size=20'])

        order_mock.assert_called_with('100', origin_snapshot_id=470,
                                      duplicate_size=250, duplicate_iops=None,
                                      duplicate_tier_level=2,
                                      duplicate_snapshot_size=20,
                                      hourly_billing_flag=True,
                                      dependent_duplicate=False)
        self.assert_no_fail(result)
        self.assertEqual(result.output,
                         'Order #24602 placed successfully!\n'
                         ' > Storage as a Service\n')

    @mock.patch('SoftLayer.BlockStorageManager.order_modified_volume')
    def test_modify_order_exception_caught(self, order_mock):
        order_mock.side_effect = ValueError('order attempt failed, noooo!')

        result = self.run_command(['block', 'volume-modify', '102', '--new-size=1000'])

        self.assertEqual(2, result.exit_code)
        self.assertEqual('Argument Error: order attempt failed, noooo!', result.exception.message)

    @mock.patch('SoftLayer.BlockStorageManager.order_modified_volume')
    def test_modify_order_order_not_placed(self, order_mock):
        order_mock.return_value = {}

        result = self.run_command(['block', 'volume-modify', '102', '--new-iops=1400'])

        self.assert_no_fail(result)
        self.assertEqual('Order could not be placed! Please verify your options and try again.\n', result.output)

    @mock.patch('SoftLayer.BlockStorageManager.order_modified_volume')
    def test_modify_order(self, order_mock):
        order_mock.return_value = {'placedOrder': {'id': 24602, 'items': [{'description': 'Storage as a Service'},
                                                                          {'description': '1000 GBs'},
                                                                          {'description': '4 IOPS per GB'}]}}

        result = self.run_command(['block', 'volume-modify', '102', '--new-size=1000', '--new-tier=4'])

        order_mock.assert_called_with('102', new_size=1000, new_iops=None, new_tier_level=4)
        self.assert_no_fail(result)
        self.assertEqual('Order #24602 placed successfully!\n > Storage as a Service\n > 1000 GBs\n > 4 IOPS per GB\n',
                         result.output)

    def test_set_password(self):
        result = self.run_command(['block', 'access-password', '1234', '--password=AAAAA'])
        self.assert_no_fail(result)

    @mock.patch('SoftLayer.BlockStorageManager.list_block_volume_limit')
    def test_volume_limit(self, list_mock):
        list_mock.return_value = [
            {
                "datacenterName": "global",
                "maximumAvailableCount": 300,
                "provisionedCount": 100
            }]

        result = self.run_command(['block', 'volume-limits'])
        self.assert_no_fail(result)

    def test_volume_limit_empty_datacenter(self):
        expect_result = {
            'dal13': 52,
            'global': 700,
            'null': 50
        }
        result = self.run_command(['block', 'volume-limits'])
        self.assert_no_fail(result)
        self.assertEqual(json.loads(result.output), expect_result)

    def test_volume_limit_datacenter(self):
        expect_result = {
            "dal13": 52
        }
        result = self.run_command(['block', 'volume-limits', '-d', 'dal13'])
        self.assert_no_fail(result)
        self.assertEqual(json.loads(result.output), expect_result)

    def test_dupe_refresh(self):
        result = self.run_command(['block', 'volume-refresh', '102', '103'])

        self.assert_no_fail(result)

    def test_dep_dupe_convert(self):
        result = self.run_command(['block', 'volume-convert', '102'])

        self.assert_no_fail(result)

    def test_volume_options(self):
        result = self.run_command(['block', 'volume-options'])

        self.assert_no_fail(result)

    @mock.patch('SoftLayer.BlockStorageManager.volume_set_note')
    def test_volume_set_note(self, set_note):
        set_note.return_value = True

        result = self.run_command(['block', 'volume-set-note', '102', '--note=testing'])

        self.assert_no_fail(result)
        self.assertIn("successfully!", result.output)

    @mock.patch('SoftLayer.BlockStorageManager.volume_set_note')
    def test_volume_not_set_note(self, set_note):
        set_note.return_value = False

        result = self.run_command(['block', 'volume-set-note', '102', '--note=testing'])

        self.assert_no_fail(result)
        self.assertIn("Note could not be set!", result.output)

    @mock.patch('SoftLayer.BlockStorageManager.get_volume_snapshot_notification_status')
    def test_snapshot_get_notification_status(self, status):
        status.side_effect = [None, 1, 0]
        expected = ['Enabled', 'Enabled', 'Disabled']

        for expect in expected:
            result = self.run_command(['block', 'snapshot-get-notification-status', '999'])
            self.assert_no_fail(result)
            self.assertIn(expect, result.output)

    def test_object_list(self):
        result = self.run_command(['block', 'object-list'])

        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Account', 'getHubNetworkStorage')

    def test_object_details(self):
        result = self.run_command(['block', 'object-storage-detail', '1234'])

        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Network_Storage_Hub_Cleversafe_Account', 'getBuckets')

    def test_object_permissions(self):
        result = self.run_command(['block', 'object-storage-permission', '1234'])

        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Network_Storage_Hub_Cleversafe_Account', 'getObject')
        self.assert_called_with('SoftLayer_Network_Storage_Hub_Cleversafe_Account', 'getEndpoints')

    def test_block_duplicate_covert_status(self):
        result = self.run_command(['block', 'duplicate-convert-status', '12345678'])

        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Network_Storage', 'getDuplicateConversionStatus')
