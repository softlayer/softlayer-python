"""
usage: sl nas [<command>] [<args>...] [options]

Manage NAS accounts

The available commands are:
  list  List NAS accounts
"""
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

        nas_accounts = account.getNasNetworkStorage(
            mask='eventCount,serviceResource[datacenter.name]')
        nas_accounts = [NestedDict(n) for n in nas_accounts]

        table = Table(['id', 'datacenter', 'size', 'username', 'password',
                       'server'])

        for nas_account in nas_accounts:
            table.add_row([
                nas_account['id'],
                nas_account['serviceResource']['datacenter'].get('name',
                                                                 blank()),
                FormattedItem(
                    nas_account.get('capacityGb', blank()),
                    "%dGB" % nas_account.get('capacityGb', 0)),
                nas_account.get('username', blank()),
                nas_account.get('password', blank()),
                nas_account.get('serviceResourceBackendIpAddress', blank())])

        return table
