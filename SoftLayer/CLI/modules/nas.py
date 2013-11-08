"""
usage: sl nas [<command>] [<args>...] [options]

Manage NAS accounts

The available commands are:
  list  List NAS accounts
"""
# :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
# :license: MIT, see LICENSE for more details.

from SoftLayer.CLI import CLIRunnable, Table, FormattedItem
from SoftLayer.CLI.helpers import NestedDict, blank


class ListNAS(CLIRunnable):
    """
usage: sl nas list [options]

List NAS accounts

Options:
"""
    action = 'list'

    def execute(self, args):
        account = self.client['Account']

        nas = account.getNasNetworkStorage(
            mask='eventCount,serviceResource[datacenter.name]')
        nas = [NestedDict(n) for n in nas]

        t = Table(['id', 'datacenter', 'size', 'username', 'password',
                   'server'])

        for n in nas:
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
