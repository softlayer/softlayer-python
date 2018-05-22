"""
    SoftLayer.tests.CLI.modules.file_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
from SoftLayer import testing

import json
import mock


class FileTests(testing.TestCase):

    def test_access_list(self):
        result = self.run_command(['file', 'access-list', '1234'])
        self.assert_no_fail(result)

    def test_authorize_host_to_volume(self):
        result = self.run_command(['file', 'access-authorize', '12345678',
                                   '--hardware-id=100', '--virtual-id=10',
                                   '--ip-address-id=192',
                                   '--ip-address=192.3.2.1',
                                   '--subnet-id=200'])

        self.assert_no_fail(result)

    def test_deauthorize_host_to_volume(self):
        result = self.run_command(['file', 'access-revoke', '12345678',
                                   '--hardware-id=100', '--virtual-id=10',
                                   '--ip-address-id=192',
                                   '--ip-address=192.3.2.1',
                                   '--subnet-id=200'])

        self.assert_no_fail(result)

    def test_volume_list(self):
        result = self.run_command(['file', 'volume-list'])

        self.assert_no_fail(result)
        self.assertEqual([
            {
                'bytes_used': None,
                'capacity_gb': 10,
                'datacenter': 'Dallas',
                'id': 1,
                'ip_addr': '127.0.0.1',
                'storage_type': 'ENDURANCE',
                'username': 'user',
                'active_transactions': None,
                'mount_addr': '127.0.0.1:/TEST',
                'rep_partner_count': None
            }],
            json.loads(result.output))

    @mock.patch('SoftLayer.FileStorageManager.list_file_volumes')
    def test_volume_count(self, list_mock):
        list_mock.return_value = [
            {'serviceResource': {'datacenter': {'name': 'dal09'}}},
            {'serviceResource': {'datacenter': {'name': 'ams01'}}},
            {'serviceResource': {'datacenter': {'name': 'ams01'}}}
        ]

        result = self.run_command(['file', 'volume-count'])

        self.assert_no_fail(result)
        self.assertEqual(
            {
                'ams01': 2,
                'dal09': 1
            },
            json.loads(result.output))

    def test_snapshot_list(self):
        result = self.run_command(['file', 'snapshot-list', '1234'])

        self.assert_no_fail(result)
        self.assertEqual([
            {
                'id': 470,
                'name': 'unit_testing_note',
                'created': '2016-07-06T07:41:19-05:00',
                'size_bytes': '42',
            }],
            json.loads(result.output))

    def test_volume_cancel(self):
        result = self.run_command([
            '--really', 'file', 'volume-cancel', '1234'])

        self.assert_no_fail(result)
        self.assertEqual('File volume with id 1234 has been marked'
                         ' for cancellation\n', result.output)
        self.assert_called_with('SoftLayer_Billing_Item', 'cancelItem',
                                args=(False, True, None))

    def test_volume_detail(self):
        result = self.run_command(['file', 'volume-detail', '1234'])

        self.assert_no_fail(result)
        self.assertEqual({
            'Username': 'username',
            'Used Space': '0B',
            'Endurance Tier': 'READHEAVY_TIER',
            'IOPs': 1000,
            'Mount Address': '127.0.0.1:/TEST',
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
            'Replicant Volumes': [[
                {'Replicant ID': 'Volume Name', '1784': 'TEST_REP_1'},
                {'Replicant ID': 'Target IP', '1784': '10.3.174.79'},
                {'Replicant ID': 'Data Center', '1784': 'wdc01'},
                {'Replicant ID': 'Schedule', '1784': 'REPLICATION_HOURLY'},
            ], [
                {'Replicant ID': 'Volume Name', '1785': 'TEST_REP_2'},
                {'Replicant ID': 'Target IP', '1785': '10.3.177.84'},
                {'Replicant ID': 'Data Center', '1785': 'dal01'},
                {'Replicant ID': 'Schedule', '1785': 'REPLICATION_DAILY'},
            ]],
            'Original Volume Properties': [
                {'Property': 'Original Volume Size',
                 'Value': '20'},
                {'Property': 'Original Volume Name',
                 'Value': 'test-original-volume-name'},
                {'Property': 'Original Snapshot Name',
                 'Value': 'test-original-snapshot-name'}
            ]
        }, json.loads(result.output))

    def test_volume_order_performance_iops_not_given(self):
        result = self.run_command(['file', 'volume-order',
                                   '--storage-type=performance', '--size=20',
                                   '--location=dal05'])

        self.assertEqual(2, result.exit_code)

    def test_volume_order_performance_snapshot_error(self):
        result = self.run_command(['file', 'volume-order',
                                   '--storage-type=performance', '--size=20',
                                   '--iops=100', '--location=dal05',
                                   '--snapshot-size=10',
                                   '--service-offering=performance'])

        self.assertEqual(2, result.exit_code)

    @mock.patch('SoftLayer.FileStorageManager.order_file_volume')
    def test_volume_order_performance(self, order_mock):
        order_mock.return_value = {
            'placedOrder': {
                'id': 478,
                'items': [
                    {'description': 'Performance Storage'},
                    {'description': 'File Storage'},
                    {'description': '0.25 IOPS per GB'},
                    {'description': '20 GB Storage Space'},
                    {'description': '10 GB Storage Space (Snapshot Space)'}]
            }
        }

        result = self.run_command(['file', 'volume-order',
                                   '--storage-type=performance', '--size=20',
                                   '--iops=100', '--location=dal05',
                                   '--snapshot-size=10'])

        self.assert_no_fail(result)
        self.assertEqual(result.output,
                         'Order #478 placed successfully!\n'
                         ' > Performance Storage\n > File Storage\n'
                         ' > 0.25 IOPS per GB\n > 20 GB Storage Space\n'
                         ' > 10 GB Storage Space (Snapshot Space)\n')

    def test_volume_order_endurance_tier_not_given(self):
        result = self.run_command(['file', 'volume-order',
                                   '--storage-type=endurance', '--size=20',
                                   '--location=dal05'])

        self.assertEqual(2, result.exit_code)

    @mock.patch('SoftLayer.FileStorageManager.order_file_volume')
    def test_volume_order_endurance(self, order_mock):
        order_mock.return_value = {
            'placedOrder': {
                'id': 478,
                'items': [
                    {'description': 'Endurance Storage'},
                    {'description': 'File Storage'},
                    {'description': '0.25 IOPS per GB'},
                    {'description': '20 GB Storage Space'},
                    {'description': '10 GB Storage Space (Snapshot Space)'}]
            }
        }

        result = self.run_command(['file', 'volume-order',
                                   '--storage-type=endurance', '--size=20',
                                   '--tier=0.25', '--location=dal05',
                                   '--snapshot-size=10'])

        self.assert_no_fail(result)
        self.assertEqual(result.output,
                         'Order #478 placed successfully!\n'
                         ' > Endurance Storage\n > File Storage\n'
                         ' > 0.25 IOPS per GB\n > 20 GB Storage Space\n'
                         ' > 10 GB Storage Space (Snapshot Space)\n')

    @mock.patch('SoftLayer.FileStorageManager.order_file_volume')
    def test_volume_order_order_not_placed(self, order_mock):
        order_mock.return_value = {}

        result = self.run_command(['file', 'volume-order',
                                   '--storage-type=endurance', '--size=20',
                                   '--tier=0.25', '--location=dal05'])

        self.assert_no_fail(result)
        self.assertEqual(result.output,
                         'Order could not be placed! Please verify '
                         'your options and try again.\n')

    def test_volume_order_hourly_billing_not_available(self):
        result = self.run_command(['file', 'volume-order',
                                   '--storage-type=endurance', '--size=20',
                                   '--tier=0.25', '--location=dal10',
                                   '--billing=hourly',
                                   '--service-offering=enterprise'])

        self.assertEqual(2, result.exit_code)

    @mock.patch('SoftLayer.FileStorageManager.order_file_volume')
    def test_volume_order_hourly_billing(self, order_mock):
        order_mock.return_value = {
            'placedOrder': {
                'id': 479,
                'items': [
                    {'description': 'Storage as a Service'},
                    {'description': 'File Storage'},
                    {'description': '20 GB Storage Space'},
                    {'description': '0.25 IOPS per GB'},
                    {'description': '10 GB Storage Space (Snapshot Space)'}]
            }
        }

        result = self.run_command(['file', 'volume-order',
                                   '--storage-type=endurance', '--size=20',
                                   '--tier=0.25', '--location=dal05',
                                   '--service-offering=storage_as_a_service',
                                   '--billing=hourly', '--snapshot-size=10'])

        self.assert_no_fail(result)
        self.assertEqual(result.output,
                         'Order #479 placed successfully!\n'
                         ' > Storage as a Service\n'
                         ' > File Storage\n'
                         ' > 20 GB Storage Space\n'
                         ' > 0.25 IOPS per GB\n'
                         ' > 10 GB Storage Space (Snapshot Space)\n')

    @mock.patch('SoftLayer.FileStorageManager.order_file_volume')
    def test_volume_order_performance_manager_error(self, order_mock):
        order_mock.side_effect = ValueError('failure!')

        result = self.run_command(['file', 'volume-order',
                                   '--storage-type=performance', '--size=20',
                                   '--iops=100', '--location=dal05'])

        self.assertEqual(2, result.exit_code)
        self.assertEqual('Argument Error: failure!', result.exception.message)

    @mock.patch('SoftLayer.FileStorageManager.order_file_volume')
    def test_volume_order_endurance_manager_error(self, order_mock):
        order_mock.side_effect = ValueError('failure!')

        result = self.run_command(['file', 'volume-order',
                                   '--storage-type=endurance', '--size=20',
                                   '--tier=0.25', '--location=dal05'])

        self.assertEqual(2, result.exit_code)
        self.assertEqual('Argument Error: failure!', result.exception.message)

    def test_enable_snapshots(self):
        result = self.run_command(['file', 'snapshot-enable', '12345678',
                                   '--schedule-type=HOURLY', '--minute=10',
                                   '--retention-count=5'])

        self.assert_no_fail(result)

    def test_disable_snapshots(self):
        result = self.run_command(['file', 'snapshot-disable', '12345678',
                                   '--schedule-type=HOURLY'])
        self.assert_no_fail(result)

    def test_list_volume_schedules(self):
        result = self.run_command([
            'file', 'snapshot-schedule-list', '12345678'])
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
        result = self.run_command(['file', 'snapshot-create', '12345678'])

        self.assert_no_fail(result)
        self.assertEqual('New snapshot created with id: 449\n', result.output)

    @mock.patch('SoftLayer.FileStorageManager.create_snapshot')
    def test_create_snapshot_unsuccessful(self, snapshot_mock):
        snapshot_mock.return_value = []

        result = self.run_command(['file', 'snapshot-create', '8', '-n=note'])

        self.assertEqual('Error occurred while creating snapshot.\n'
                         'Ensure volume is not failed over or in another '
                         'state which prevents taking snapshots.\n',
                         result.output)

    def test_snapshot_restore(self):
        result = self.run_command(['file', 'snapshot-restore', '12345678',
                                   '--snapshot-id=87654321'])

        self.assert_no_fail(result)
        self.assertEqual(result.output, 'File volume 12345678 is being'
                         ' restored using snapshot 87654321\n')

    def test_delete_snapshot(self):
        result = self.run_command(['file', 'snapshot-delete', '12345678'])

        self.assert_no_fail(result)

    @mock.patch('SoftLayer.FileStorageManager.order_snapshot_space')
    def test_snapshot_order_order_not_placed(self, order_mock):
        order_mock.return_value = {}

        result = self.run_command(['file', 'snapshot-order', '1234',
                                   '--capacity=10', '--tier=0.25'])

        self.assert_no_fail(result)
        self.assertEqual(result.output,
                         'Order could not be placed! Please verify '
                         'your options and try again.\n')

    @mock.patch('SoftLayer.FileStorageManager.order_snapshot_space')
    def test_snapshot_order_performance_manager_error(self, order_mock):
        order_mock.side_effect = ValueError('failure!')

        result = self.run_command(['file', 'snapshot-order', '1234',
                                   '--capacity=10', '--tier=0.25'])

        self.assertEqual(2, result.exit_code)
        self.assertEqual('Argument Error: failure!', result.exception.message)

    @mock.patch('SoftLayer.FileStorageManager.order_snapshot_space')
    def test_snapshot_order(self, order_mock):
        order_mock.return_value = {
            'placedOrder': {
                'id': 8702,
                'items': [{'description':
                           '10 GB Storage Space (Snapshot Space)'}],
                'status': 'PENDING_APPROVAL',
            }
        }

        result = self.run_command(['file', 'snapshot-order', '1234',
                                   '--capacity=10', '--tier=0.25'])

        self.assert_no_fail(result)
        self.assertEqual(result.output,
                         'Order #8702 placed successfully!\n'
                         ' > 10 GB Storage Space (Snapshot Space)\n'
                         ' > Order status: PENDING_APPROVAL\n')

    def test_snapshot_cancel(self):
        result = self.run_command(['--really',
                                   'file', 'snapshot-cancel', '1234'])

        self.assert_no_fail(result)
        self.assertEqual('File volume with id 1234 has been marked'
                         ' for snapshot cancellation\n', result.output)
        self.assert_called_with('SoftLayer_Billing_Item', 'cancelItem',
                                args=(False, True, None))

    def test_replicant_failover(self):
        result = self.run_command(['file', 'replica-failover', '12345678',
                                   '--replicant-id=5678', '--immediate'])

        self.assert_no_fail(result)
        self.assertEqual('Failover to replicant is now in progress.\n',
                         result.output)

    @mock.patch('SoftLayer.FileStorageManager.failover_to_replicant')
    def test_replicant_failover_unsuccessful(self, failover_mock):
        failover_mock.return_value = False

        result = self.run_command(['file', 'replica-failover', '12345678',
                                   '--replicant-id=5678'])

        self.assertEqual('Failover operation could not be initiated.\n',
                         result.output)

    def test_replicant_failback(self):
        result = self.run_command(['file', 'replica-failback', '12345678',
                                   '--replicant-id=5678'])

        self.assert_no_fail(result)
        self.assertEqual('Failback from replicant is now in progress.\n',
                         result.output)

    @mock.patch('SoftLayer.FileStorageManager.failback_from_replicant')
    def test_replicant_failback_unsuccessful(self, failback_mock):
        failback_mock.return_value = False

        result = self.run_command(['file', 'replica-failback', '12345678',
                                   '--replicant-id=5678'])

        self.assertEqual('Failback operation could not be initiated.\n',
                         result.output)

    @mock.patch('SoftLayer.FileStorageManager.order_replicant_volume')
    def test_replicant_order_order_not_placed(self, order_mock):
        order_mock.return_value = {}

        result = self.run_command(['file', 'replica-order', '100',
                                   '--snapshot-schedule=DAILY',
                                   '--location=dal05'])

        self.assert_no_fail(result)
        self.assertEqual(result.output,
                         'Order could not be placed! Please verify '
                         'your options and try again.\n')

    @mock.patch('SoftLayer.FileStorageManager.order_replicant_volume')
    def test_replicant_order(self, order_mock):
        order_mock.return_value = {
            'placedOrder': {
                'id': 77309,
                'items': [
                    {'description': 'Endurance Storage'},
                    {'description': '2 IOPS per GB'},
                    {'description': 'File Storage'},
                    {'description': '20 GB Storage Space'},
                    {'description': '10 GB Storage Space (Snapshot Space)'},
                    {'description': '20 GB Storage Space Replicant of: TEST'},
                ],
            }
        }

        result = self.run_command(['file', 'replica-order', '100',
                                   '--snapshot-schedule=DAILY',
                                   '--location=dal05', '--tier=2'])

        self.assert_no_fail(result)
        self.assertEqual(result.output,
                         'Order #77309 placed successfully!\n'
                         ' > Endurance Storage\n'
                         ' > 2 IOPS per GB\n'
                         ' > File Storage\n'
                         ' > 20 GB Storage Space\n'
                         ' > 10 GB Storage Space (Snapshot Space)\n'
                         ' > 20 GB Storage Space Replicant of: TEST\n')

    def test_replication_locations(self):
        result = self.run_command(['file', 'replica-locations', '1234'])
        self.assert_no_fail(result)
        self.assertEqual(
            {
                '12345': 'Dallas 05',
            },
            json.loads(result.output))

    @mock.patch('SoftLayer.FileStorageManager.get_replication_locations')
    def test_replication_locations_unsuccessful(self, locations_mock):
        locations_mock.return_value = False
        result = self.run_command(['file', 'replica-locations', '1234'])
        self.assert_no_fail(result)
        self.assertEqual('No data centers compatible for replication.\n',
                         result.output)

    def test_replication_partners(self):
        result = self.run_command(['file', 'replica-partners', '1234'])
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

    @mock.patch('SoftLayer.FileStorageManager.get_replication_partners')
    def test_replication_partners_unsuccessful(self, partners_mock):
        partners_mock.return_value = False
        result = self.run_command(['file', 'replica-partners', '1234'])
        self.assertEqual(
            'There are no replication partners for the given volume.\n',
            result.output)

    @mock.patch('SoftLayer.FileStorageManager.order_duplicate_volume')
    def test_duplicate_order_exception_caught(self, order_mock):
        order_mock.side_effect = ValueError('order attempt failed, oh noooo!')

        result = self.run_command(['file', 'volume-duplicate', '100'])

        self.assertEqual(2, result.exit_code)
        self.assertEqual('Argument Error: order attempt failed, oh noooo!',
                         result.exception.message)

    @mock.patch('SoftLayer.FileStorageManager.order_duplicate_volume')
    def test_duplicate_order_order_not_placed(self, order_mock):
        order_mock.return_value = {}

        result = self.run_command(['file', 'volume-duplicate', '100',
                                   '--duplicate-iops=1400'])

        self.assert_no_fail(result)
        self.assertEqual(result.output,
                         'Order could not be placed! Please verify '
                         'your options and try again.\n')

    @mock.patch('SoftLayer.FileStorageManager.order_duplicate_volume')
    def test_duplicate_order(self, order_mock):
        order_mock.return_value = {
            'placedOrder': {
                'id': 24602,
                'items': [{'description': 'Storage as a Service'}]
            }
        }

        result = self.run_command(['file', 'volume-duplicate', '100',
                                   '--origin-snapshot-id=470',
                                   '--duplicate-size=250',
                                   '--duplicate-tier=2',
                                   '--duplicate-snapshot-size=20'])

        self.assert_no_fail(result)
        self.assertEqual(result.output,
                         'Order #24602 placed successfully!\n'
                         ' > Storage as a Service\n')

    @mock.patch('SoftLayer.FileStorageManager.order_duplicate_volume')
    def test_duplicate_order_hourly_billing(self, order_mock):
        order_mock.return_value = {
            'placedOrder': {
                'id': 24602,
                'items': [{'description': 'Storage as a Service'}]
            }
        }

        result = self.run_command(['file', 'volume-duplicate', '100',
                                   '--origin-snapshot-id=470',
                                   '--duplicate-size=250',
                                   '--duplicate-tier=2', '--billing=hourly',
                                   '--duplicate-snapshot-size=20'])

        order_mock.assert_called_with('100', origin_snapshot_id=470,
                                      duplicate_size=250, duplicate_iops=None,
                                      duplicate_tier_level=2,
                                      duplicate_snapshot_size=20,
                                      hourly_billing_flag=True)
        self.assert_no_fail(result)
        self.assertEqual(result.output,
                         'Order #24602 placed successfully!\n'
                         ' > Storage as a Service\n')

    @mock.patch('SoftLayer.FileStorageManager.order_modified_volume')
    def test_modify_order_exception_caught(self, order_mock):
        order_mock.side_effect = ValueError('order attempt failed, noooo!')

        result = self.run_command(['file', 'volume-modify', '102', '--new-size=1000'])

        self.assertEqual(2, result.exit_code)
        self.assertEqual('Argument Error: order attempt failed, noooo!', result.exception.message)

    @mock.patch('SoftLayer.FileStorageManager.order_modified_volume')
    def test_modify_order_order_not_placed(self, order_mock):
        order_mock.return_value = {}

        result = self.run_command(['file', 'volume-modify', '102', '--new-iops=1400'])

        self.assert_no_fail(result)
        self.assertEqual('Order could not be placed! Please verify your options and try again.\n', result.output)

    @mock.patch('SoftLayer.FileStorageManager.order_modified_volume')
    def test_modify_order(self, order_mock):
        order_mock.return_value = {'placedOrder': {'id': 24602, 'items': [{'description': 'Storage as a Service'},
                                                                          {'description': '1000 GBs'},
                                                                          {'description': '4 IOPS per GB'}]}}

        result = self.run_command(['file', 'volume-modify', '102', '--new-size=1000', '--new-tier=4'])

        order_mock.assert_called_with('102', new_size=1000, new_iops=None, new_tier_level=4)
        self.assert_no_fail(result)
        self.assertEqual('Order #24602 placed successfully!\n > Storage as a Service\n > 1000 GBs\n > 4 IOPS per GB\n',
                         result.output)
