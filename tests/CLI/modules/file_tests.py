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
        self.assertEqual([
            {
                'username': 'joe',
                'name': 'test-server.example.com',
                'type': 'VIRTUAL',
                'host_iqn': 'test-server',
                'password': '12345',
                'private_ip_address': '10.0.0.1',
                'id': 1234,
            },
            {
                'username': 'joe',
                'name': 'test-server.example.com',
                'type': 'HARDWARE',
                'host_iqn': 'test-server',
                'password': '12345',
                'private_ip_address': '10.0.0.2',
                'id': 1234,
            },
            {
                'username': 'joe',
                'name': '10.0.0.1/24 (backend subnet)',
                'type': 'SUBNET',
                'host_iqn': 'test-server',
                'password': '12345',
                'private_ip_address': None,
                'id': 1234,
            },
            {
                'username': 'joe',
                'name': '10.0.0.1 (backend ip)',
                'type': 'IP',
                'host_iqn': 'test-server',
                'password': '12345',
                'private_ip_address': None,
                'id': 1234,
            }],
            json.loads(result.output),)

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
                'mount_addr': '127.0.0.1:/TEST'
            }],
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
            'Endurance Tier': '2 IOPS per GB',
            'IOPs': 1000,
            'Mount Address': '127.0.0.1:/TEST',
            'Snapshot Capacity (GB)': '10',
            'Snapshot Used (Bytes)': 1024,
            'Capacity (GB)': '20GB',
            'Target IP': '10.1.2.3',
            'Data Center': 'dal05',
            'Type': 'ENDURANCE',
            'ID': 100,
            '# of Active Transactions': '0',
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
            ]]
        }, json.loads(result.output))

    def test_volume_order_performance_iops_not_given(self):
        result = self.run_command(['file', 'volume-order',
                                   '--storage-type=performance', '--size=20',
                                   '--os-type=linux', '--location=dal05'])

        self.assertEqual(2, result.exit_code)

    def test_volume_order_performance_iops_out_of_range(self):
        result = self.run_command(['file', 'volume-order',
                                   '--storage-type=performance', '--size=20',
                                   '--iops=80000', '--os-type=linux',
                                   '--location=dal05'])

        self.assertEqual(2, result.exit_code)

    def test_volume_order_performance_iops_not_multiple_of_100(self):
        result = self.run_command(['file', 'volume-order',
                                   '--storage-type=performance', '--size=20',
                                   '--iops=122', '--os-type=linux',
                                   '--location=dal05'])

        self.assertEqual(2, result.exit_code)

    def test_volume_order_performance_snapshot_error(self):
        result = self.run_command(['file', 'volume-order',
                                   '--storage-type=performance', '--size=20',
                                   '--iops=100', '--os-type=linux',
                                   '--location=dal05', '--snapshot-size=10'])

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
                    {'description': '20 GB Storage Space'}]
            }
        }

        result = self.run_command(['file', 'volume-order',
                                   '--storage-type=performance', '--size=20',
                                   '--iops=100', '--os-type=linux',
                                   '--location=dal05'])

        self.assert_no_fail(result)
        self.assertEqual(result.output,
                         'Order #478 placed successfully!\n'
                         ' > Performance Storage\n > File Storage\n'
                         ' > 0.25 IOPS per GB\n > 20 GB Storage Space\n')

    def test_volume_order_endurance_tier_not_given(self):
        result = self.run_command(['file', 'volume-order',
                                   '--storage-type=endurance', '--size=20',
                                   '--os-type=linux', '--location=dal05'])

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
                                   '--tier=0.25', '--os-type=linux',
                                   '--location=dal05', '--snapshot-size=10'])

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
                                   '--tier=0.25', '--os-type=linux',
                                   '--location=dal05'])

        self.assert_no_fail(result)
        self.assertEqual(result.output,
                         'Order could not be placed! Please verify '
                         'your options and try again.\n')

    def test_enable_snapshots(self):
        result = self.run_command(['file', 'snapshot-enable', '12345678',
                                   '--schedule-type=HOURLY', '--minute=10',
                                   '--retention-count=5'])

        self.assert_no_fail(result)

    def test_disable_snapshots(self):
        result = self.run_command(['file', 'snapshot-disable', '12345678',
                                   '--schedule-type=HOURLY'])
        self.assert_no_fail(result)

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
