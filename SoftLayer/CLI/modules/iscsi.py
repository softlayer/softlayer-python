"""
usage: sl iscsi [<command>] [<args>...] [options]

Manage iSCSI targets

The available commands are:
  list                 List iSCSI targets
  create               Create iSCSI target
  detail               Output details about iSCSI
  cancel               cancel iSCSI target
  create_snapshot_space Orders space for snapshots
  create_snapshot      Create snapshot of iSCSI
  delete_snapshot      Delete iSCSI snapshot
  restore_volume       Restores volume from existing snapshot
  list_snapshots       List Snapshots of given iscsi

"""
from SoftLayer.CLI import (CLIRunnable, Table, no_going_back, FormattedItem)
from SoftLayer.CLI.helpers import (
    CLIAbort, ArgumentError, NestedDict, blank, resolve_id, KeyValueTable)
from SoftLayer import ISCSIManager


class ListISCSI(CLIRunnable):

    """
    usage: sl iscsi list [options]

List iSCSI accounts
"""
    action = 'list'

    def execute(self, args):
        account = self.client['Account']

        iscsi_list = account.getIscsiNetworkStorage(
            mask='eventCount,serviceResource[datacenter.name]')
        iscsi_list = [NestedDict(n) for n in iscsi_list]

        table = Table([
            'id',
            'datacenter',
            'size',
            'username',
            'password',
            'server'
        ])

        for iscsi in iscsi_list:
            table.add_row([
                iscsi['id'],
                iscsi['serviceResource']['datacenter'].get('name', blank()),
                FormattedItem(
                    iscsi.get('capacityGb', blank()),
                    "%dGB" % iscsi.get('capacityGb', 0)),
                iscsi.get('username', blank()),
                iscsi.get('password', blank()),
                iscsi.get('serviceResourceBackendIpAddress', blank())])

        return table


class CreateISCSI(CLIRunnable):

    """
    usage: sl iscsi create --size=SIZE --dc=DC [options]

    Order/create an iSCSI storage.

    Required:
     --size=SIZE       Size of the iSCSI volume to create
     --dc=DC           Datacenter to use to create volume in
    Optional:
     --zero-recurring  Prefer <$1 recurring fee
     """
    action = 'create'
    options = ['confirm']
    required_params = ['--size', '--dc']

    def execute(self, args):
        iscsi_mgr = ISCSIManager(self.client)

        self._validate_create_args(args)
        size = int(args.get('--size')),
        location = str(args.get('--dc')),
        zero_recurring = args.get('--zero-recurring', False)
        iscsi_mgr.create_iscsi(size=size, location=location,
                               zero_recurring=zero_recurring)

    def _validate_create_args(self, args):
        """ Raises an ArgumentError if the given arguments are not valid """
        invalid_args = [k for k in self.required_params if args.get(k) is None]
        if invalid_args:
            raise ArgumentError('Missing required options: %s'
                                % ','.join(invalid_args))


class CancelISCSI(CLIRunnable):

    """
usage: sl iscsi cancel <identifier> [options]

Cancel iSCSI Storage

options :
--immediate    Cancels the iSCSI immediately (instead of on the billing
             anniversary)
--reason=REASON    An optional cancellation reason.

"""
    action = 'cancel'
    options = ['confirm']

    def execute(self, args):
        iscsi_mgr = ISCSIManager(self.client)
        iscsi_id = resolve_id(
            iscsi_mgr.resolve_ids,
            args.get('<identifier>'),
            'iSCSI')

        immediate = args.get('--immediate', False)

        reason = args.get('--reason')
        if args['--really'] or no_going_back(iscsi_id):
            iscsi_mgr.cancel_iscsi(iscsi_id, reason, immediate)
        else:
            CLIAbort('Aborted')


class ISCSIDetails(CLIRunnable):

    """
usage: sl iscsi detail [--password] <identifier> [options]

Get details for a iSCSI

Options:
  --password  Show password


"""
    action = 'detail'

    def execute(self, args):
        iscsi_mgr = ISCSIManager(self.client)
        table = KeyValueTable(['Name', 'Value'])
        table.align['Name'] = 'r'
        table.align['Value'] = 'l'

        iscsi_id = resolve_id(
            iscsi_mgr.resolve_ids,
            args.get('<identifier>'),
            'iSCSI')
        result = iscsi_mgr.get_iscsi(iscsi_id)
        result = NestedDict(result)

        table.add_row(['id', result['id']])
        table.add_row(['serviceResourceName', result['serviceResourceName']])
        table.add_row(['createDate', result['createDate']])
        table.add_row(['nasType', result['nasType']])
        table.add_row(['capacityGb', result['capacityGb']])
        if result['snapshotCapacityGb']:
            table.add_row(['snapshotCapacityGb', result['snapshotCapacityGb']])
        table.add_row(['mountableFlag', result['mountableFlag']])
        table.add_row(
            ['serviceResourceBackendIpAddress',
             result['serviceResourceBackendIpAddress']])
        table.add_row(['price', result['billingItem']['recurringFee']])
        table.add_row(['BillingItemId', result['billingItem']['id']])
        if result.get('notes'):
            table.add_row(['notes', result['notes']])

        if args.get('--password'):
            pass_table = Table(['username', 'password'])
            pass_table.add_row([result['username'], result['password']])
            table.add_row(['users', pass_table])

        return table


class ISCSICreateSnapshot(CLIRunnable):

    """
usage: sl iscsi create_snapshot <identifier> [options]

create an iSCSI snapshot.

Options:
--notes=NOTE    An optional note

"""
    action = 'create_snapshot'

    def execute(self, args):
        iscsi_mgr = ISCSIManager(self.client)
        iscsi_id = resolve_id(iscsi_mgr.resolve_ids,
                              args.get('<identifier>'),
                              'iSCSI')
        notes = args.get('--notes')
        iscsi_mgr.create_snapshot(iscsi_id, notes)


class CreateIscsiSpace(CLIRunnable):

    """
usage: sl iscsi create_snapshot_space <identifier> [options]

Orders iSCSI snapshot space.

Required :
--capacity=Capacity Snapshot Capacity
"""

    action = 'create_snapshot_space'
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
usage: sl iscsi delete_snapshot <identifier> [options]

Delete iSCSI snapshot.

"""
    action = 'delete_snapshot'

    def execute(self, args):
        iscsi_mgr = ISCSIManager(self.client)
        snapshot_id = resolve_id(
            iscsi_mgr.resolve_ids,
            args.get('<identifier>'),
            'Snapshot')
        iscsi_mgr.delete_snapshot(snapshot_id)


class RestoreVolumeFromSnapshot(CLIRunnable):

    """
usage: sl iscsi restore_volume <volume_identifier> <snapshot_identifier>

restores volume from existing snapshot.

"""
    action = 'restore_volume'

    def execute(self, args):
        iscsi_mgr = ISCSIManager(self.client)
        volume_id = resolve_id(
            iscsi_mgr.resolve_ids, args.get('<volume_identifier>'), 'iSCSI')
        snapshot_id = resolve_id(iscsi_mgr.resolve_ids,
                                 args.get('<snapshot_identifier>'), 'Snapshot')
        iscsi_mgr.restore_from_snapshot(volume_id, snapshot_id)


class ListISCSISnapshots(CLIRunnable):

    """
    usage: sl iscsi list_snapshots <identifier>

List iSCSI Snapshots
"""
    action = 'list_snapshots'

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
