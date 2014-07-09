"""
usage: sl iscsi [<command>] [<args>...] [options]

Manage, order, delete iSCSI targets

The available commands are:
  cancel  Cancel an existing iSCSI target
  create  Order and create an iSCSI target
  detail  Output details about an iSCSI
  list    List iSCSI targets on the account

For several commands, <identifier> will be asked for. This will be the id
for iSCSI target.
"""
# from SoftLayer.CLI import (CLIRunnable, Table, no_going_back, FormattedItem)
import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers
from SoftLayer import utils


class ListISCSIs(environment.CLIRunnable):

    """
usage: sl iscsi list [options]

List iSCSI targets
"""
    action = 'list'

    def execute(self, args):
        iscsi_mgr = SoftLayer.ISCSIManager(self.client)
        iscsi_list = iscsi_mgr.list_iscsi()
        iscsi_list = [utils.NestedDict(n) for n in iscsi_list]
        table = formatting.Table([
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
                iscsi['serviceResource']['datacenter'].get('name',
                                                           formatting.blank()),
                formatting.FormattedItem(
                    iscsi.get('capacityGb', formatting.blank()),
                    "%dGB" % iscsi.get('capacityGb', 0)),
                iscsi.get('username', formatting.blank()),
                iscsi.get('password', formatting.blank()),
                iscsi.get('serviceResourceBackendIpAddress',
                          formatting.blank())])
        return table


class CreateISCSI(environment.CLIRunnable):

    """
usage: sl iscsi create [options]

Orders and creates an iSCSI target.

Examples:
    sl iscsi create --size=1 --datacenter=dal05
    sl iscsi create --size 1 -d dal05
    sl iscsi create -s 1 -d dal05

Required:
  -s, --size=SIZE       Size of the iSCSI volume to create
  -d, --datacenter=DC   Datacenter shortname (sng01, dal05, ...)
"""
    action = 'create'
    options = ['confirm']
    required_params = ['--size', '--datacenter']

    def execute(self, args):
        iscsi_mgr = SoftLayer.ISCSIManager(self.client)
        self._validate_create_args(args)
        size, location = self._parse_create_args(args)
        iscsi_mgr.create_iscsi(size=size, location=location)

    def _parse_create_args(self, args):
        """ Converts CLI arguments to arguments that can be passed into
            ISCSIManager.create_iscsi.
        :param dict args: CLI arguments
        """
        size = args['--size']
        location = args['--datacenter']
        return int(size), str(location)

    def _validate_create_args(self, args):
        """ Raises an ArgumentError if the given arguments are not valid """
        invalid_args = [k for k in self.required_params if args.get(k) is None]
        if invalid_args:
            raise exceptions.ArgumentError('Missing required options: %s'
                                           % ','.join(invalid_args))


class CancelISCSI(environment.CLIRunnable):

    """
usage: sl iscsi cancel <identifier> [options]

Cancel existing iSCSI

Examples:
    sl iscsi cancel 12345
    sl iscsi cancel 12345 --immediate
    sl iscsi cancel 12345 --immediate --reason='no longer needed'

options :
  --immediate    Cancels the iSCSI immediately (instead of on the billing
                    anniversary)
  --reason=REASON    An optional reason for cancellation.
"""
    action = 'cancel'
    options = ['confirm']

    def execute(self, args):
        iscsi_mgr = SoftLayer.ISCSIManager(self.client)
        iscsi_id = helpers.resolve_id(
            iscsi_mgr.resolve_ids,
            args.get('<identifier>'),
            'iSCSI')

        immediate = args.get('--immediate', False)

        reason = args.get('--reason')
        if args['--really'] or formatting.no_going_back(iscsi_id):
            iscsi_mgr.cancel_iscsi(iscsi_id, reason, immediate)
        else:
            raise exceptions.CLIAbort('Aborted')


class ISCSIDetails(environment.CLIRunnable):

    """
usage: sl iscsi detail [--password] <identifier> [options]

Get details for an iSCSI

Examples:
    sl iscsi detail 12345
    sl iscsi detail 12345 --password

Options:
  --password  Show credentials to access the iSCSI target
"""
    action = 'detail'

    def execute(self, args):
        iscsi_mgr = SoftLayer.ISCSIManager(self.client)
        table = formatting.KeyValueTable(['Name', 'Value'])
        table.align['Name'] = 'r'
        table.align['Value'] = 'l'

        iscsi_id = helpers.resolve_id(
            iscsi_mgr.resolve_ids,
            args.get('<identifier>'),
            'iSCSI')
        result = iscsi_mgr.get_iscsi(iscsi_id)
        result = utils.NestedDict(result)

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
            pass_table = formatting.Table(['username', 'password'])
            pass_table.add_row([result['username'], result['password']])
            table.add_row(['users', pass_table])

        return table
