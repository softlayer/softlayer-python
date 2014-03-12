"""
usage: sl iscsi [<command>] [<args>...] [options]

Manage iSCSI targets

The available commands are:
  list  List iSCSI targets
"""
# :license: MIT, see LICENSE for more details.

from SoftLayer.CLI import CLIRunnable, Table, FormattedItem
from SoftLayer.CLI.helpers import NestedDict, blank


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
        iscsi_list = [NestedDict(iscsi) for iscsi in iscsi_list]

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
