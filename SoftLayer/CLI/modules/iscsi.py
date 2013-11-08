"""
usage: sl iscsi [<command>] [<args>...] [options]

Manage iSCSI targets

The available commands are:
  list  List iSCSI targets
"""
# :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
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

        iscsi = account.getIscsiNetworkStorage(
            mask='eventCount,serviceResource[datacenter.name]')
        iscsi = [NestedDict(n) for n in iscsi]

        t = Table([
            'id',
            'datacenter',
            'size',
            'username',
            'password',
            'server'
        ])

        for n in iscsi:
            t.add_row([
                n['id'],
                n['serviceResource']['datacenter'].get('name', blank()),
                FormattedItem(
                    n.get('capacityGb', blank()),
                    "%dGB" % n.get('capacityGb', 0)),
                n.get('username', blank()),
                n.get('password', blank()),
                n.get('serviceResourceBackendIpAddress', blank())])

        return t
