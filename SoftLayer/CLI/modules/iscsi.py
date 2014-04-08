"""
usage: sl iscsi [<command>] [<args>...] [options]

Manage iSCSI targets

The available commands are:
  cancel  Cancel iSCSI target
  create  Create iSCSI target
  detail  Output details about iSCSI
  list    List iSCSI targets

For several commands, <identifier> will be asked for. This can be the id
for iSCSI.
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
    usage: sl iscsi create [options]

    Order/create an iSCSI storage.

    Required:
     -s, --size=SIZE       Size of the iSCSI volume to create
     -d, --datacenter=DC   Datacenter shortname (sng01, dal05, ...)
     """
    action = 'create'
    options = ['confirm']
    required_params = ['--size', '--datacenter']

    def execute(self, args):
        iscsi_mgr = ISCSIManager(self.client)
        self._validate_create_args(args)
        size, location = self._parse_create_args(args)
        iscsi_mgr.create_iscsi(size=size, location=location)

    def _parse_create_args(self, args):
        """ Converts CLI arguments to arguments that can be passed into
            ISCSIManager.create_iscsi.
        :param dict args: CLI arguments
        """
        size = int(args['--size'])
        location = str(args['--datacenter'])
        return size, location

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
