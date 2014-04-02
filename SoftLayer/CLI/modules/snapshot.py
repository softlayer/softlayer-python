"""
usage: sl snapshot [<command>] [<args>...] [options]

Manage iSCSI snapshots

The available commands are:
  create          Create snapshot of iSCSI
  create_space    Orders space for snapshots
  delete          Delete iSCSI snapshot
  list            List snpshots of given iSCSI
  restore_volume  Restores volume from existing snapshot

"""
from SoftLayer.CLI import (CLIRunnable, Table)
from SoftLayer.CLI.helpers import (
    ArgumentError, NestedDict,
    resolve_id)
from SoftLayer import ISCSIManager


class ISCSICreateSnapshot(CLIRunnable):

    """
usage: sl snapshot create <identifier> [options]

create an iSCSI snapshot.

Options:
  --notes=NOTE    An optional note

"""
    action = 'create'

    def execute(self, args):
        iscsi_mgr = ISCSIManager(self.client)
        iscsi_id = resolve_id(
            iscsi_mgr.resolve_ids,
            args.get('<identifier>'),
            'iSCSI')
        notes = args.get('--notes')
        iscsi_mgr.create_snapshot(iscsi_id, notes)


class CreateIscsiSpace(CLIRunnable):

    """
usage: sl snapshot create_space <identifier> [options]

Orders iSCSI snapshot space.

Required :
  --capacity=Capacity Snapshot Capacity
"""

    action = 'create_space'
    required_params = ['--capacity']

    def execute(self, args):
        iscsi_mgr = ISCSIManager(self.client)
        invalid_args = [k for k in self.required_params if args.get(k) is None]
        if invalid_args:
            raise ArgumentError('Missing required options: %s'
                                % ','.join(invalid_args))
        iscsi_id = resolve_id(
            iscsi_mgr.resolve_ids,
            args.get('<identifier>'),
            'iSCSI')
        capacity = args.get('--capacity')
        iscsi_mgr.create_snapshot_space(iscsi_id, capacity)


class ISCSIDeleteSnapshot(CLIRunnable):

    """
usage: sl snapshot delete <identifier> [options]

Delete iSCSI snapshot.

"""
    action = 'delete'

    def execute(self, args):
        iscsi_mgr = ISCSIManager(self.client)
        snapshot_id = resolve_id(
            iscsi_mgr.resolve_ids,
            args.get('<identifier>'),
            'Snapshot')
        iscsi_mgr.delete_snapshot(snapshot_id)


class RestoreVolumeFromSnapshot(CLIRunnable):

    """
usage: sl snapshot restore_volume <volume_identifier> <snapshot_identifier>

restores volume from existing snapshot.

"""
    action = 'restore_volume'

    def execute(self, args):
        iscsi_mgr = ISCSIManager(self.client)
        volume_id = resolve_id(
            iscsi_mgr.resolve_ids, args.get('<volume_identifier>'), 'iSCSI')
        snapshot_id = resolve_id(
            iscsi_mgr.resolve_ids,
            args.get('<snapshot_identifier>'),
            'Snapshot')
        iscsi_mgr.restore_from_snapshot(volume_id, snapshot_id)


class ListISCSISnapshots(CLIRunnable):

    """
usage: sl snapshot list <identifier>

List iSCSI Snapshots
"""
    action = 'list'

    def execute(self, args):
        iscsi_mgr = ISCSIManager(self.client)
        iscsi_id = resolve_id(
            iscsi_mgr.resolve_ids, args.get('<identifier>'), 'iSCSI')
        iscsi = self.client['Network_Storage_Iscsi']
        snapshots = iscsi.getPartnerships(
            mask='volumeId,partnerVolumeId,createDate,type', id=iscsi_id)
        snapshots = [NestedDict(n) for n in snapshots]

        table = Table([
            'id',
            'createDate',
            'name',
            'description',
        ])

        for snapshot in snapshots:
            table.add_row([
                snapshot['partnerVolumeId'],
                snapshot['createDate'],
                snapshot['type']['name'],
                snapshot['type']['description'],
                ])
        return table
