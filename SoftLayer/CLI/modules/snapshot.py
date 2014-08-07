"""
usage: sl snapshot [<command>] [<args>...] [options]

Manage, order, delete iSCSI snapshots

The available commands are:
  cancel          Cancel an iSCSI snapshot
  create          Create a snapshot of given iSCSI volume
  create-space    Orders space for storing snapshots
  list            List snpshots of given iSCSI
  restore-volume  Restores volume from existing snapshot

For several commands <identifier> will be asked for.This can be the id
of iSCSI volume or iSCSI snapshot.
"""
import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers
from SoftLayer import utils


class CreateSnapshot(environment.CLIRunnable):

    """
usage: sl snapshot create <identifier> [options]

Create a snapshot of the iSCSI volume.

Examples:
    sl snapshot create 123456 --note='Backup'
    sl snapshot create 123456

Options:
  --notes=NOTE    An optional snapshot's note

"""
    action = 'create'

    def execute(self, args):
        iscsi_mgr = SoftLayer.ISCSIManager(self.client)
        iscsi_id = helpers.resolve_id(iscsi_mgr.resolve_ids,
                                      args.get('<identifier>'),
                                      'iSCSI')
        notes = args.get('--notes')
        iscsi_mgr.create_snapshot(iscsi_id, notes)


class CreateSnapshotSpace(environment.CLIRunnable):

    """
usage: sl snapshot create-space <identifier> [options]

Orders snapshot space for given iSCSI.

Examples:
    sl snapshot create-space 123456 --capacity=20

Required :
  --capacity=CAPACITY Size of snapshot space to create
"""

    action = 'create-space'
    required_params = ['--capacity']

    def execute(self, args):
        iscsi_mgr = SoftLayer.ISCSIManager(self.client)
        invalid_args = [k for k in self.required_params if args.get(k) is None]
        if invalid_args:
            raise exceptions.ArgumentError('Missing required options: %s'
                                           % ','.join(invalid_args))
        iscsi_id = helpers.resolve_id(iscsi_mgr.resolve_ids,
                                      args.get('<identifier>'),
                                      'iSCSI')
        capacity = args.get('--capacity')
        iscsi_mgr.create_snapshot_space(iscsi_id, capacity)


class CancelSnapshot(environment.CLIRunnable):

    """
usage: sl snapshot cancel <identifier> [options]

Cancel/Delete iSCSI snapshot.

"""
    action = 'cancel'

    def execute(self, args):
        iscsi_mgr = SoftLayer.ISCSIManager(self.client)
        snapshot_id = helpers.resolve_id(iscsi_mgr.resolve_ids,
                                         args.get('<identifier>'),
                                         'Snapshot')
        iscsi_mgr.delete_snapshot(snapshot_id)


class RestoreVolumeFromSnapshot(environment.CLIRunnable):

    """
usage: sl snapshot restore-volume <volume_identifier> <snapshot_identifier>

restores volume from existing snapshot.

"""
    action = 'restore-volume'

    def execute(self, args):
        iscsi_mgr = SoftLayer.ISCSIManager(self.client)
        volume_id = helpers.resolve_id(iscsi_mgr.resolve_ids,
                                       args.get('<volume_identifier>'),
                                       'iSCSI')
        snapshot_id = helpers.resolve_id(iscsi_mgr.resolve_ids,
                                         args.get('<snapshot_identifier>'),
                                         'Snapshot')
        iscsi_mgr.restore_from_snapshot(volume_id, snapshot_id)


class ListSnapshots(environment.CLIRunnable):

    """
usage: sl snapshot list <identifier>

List iSCSI Snapshots
"""
    action = 'list'

    def execute(self, args):
        iscsi_mgr = SoftLayer.ISCSIManager(self.client)
        iscsi_id = helpers.resolve_id(iscsi_mgr.resolve_ids,
                                      args.get('<identifier>'),
                                      'iSCSI')
        iscsi = self.client['Network_Storage_Iscsi']
        snapshots = iscsi.getPartnerships(
            mask='volumeId,partnerVolumeId,createDate,type', id=iscsi_id)
        snapshots = [utils.NestedDict(n) for n in snapshots]

        table = formatting.Table([
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
