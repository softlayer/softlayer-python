"""
usage: sl nas [<command>] [<args>...] [options]

Manage NAS accounts

The available commands are:
  list  List NAS accounts
"""
# :license: MIT, see LICENSE for more details.

from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer import utils


class ListNAS(environment.CLIRunnable):
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

        table = formatting.Table(['id', 'datacenter', 'size', 'username',
                                  'password', 'server'])

        for nas_account in nas_accounts:
            table.add_row([
                nas_account['id'],
                utils.lookup(nas_account,
                             'serviceResource',
                             'datacenter',
                             'name') or formatting.blank(),
                formatting.FormattedItem(
                    nas_account.get('capacityGb', formatting.blank()),
                    "%dGB" % nas_account.get('capacityGb', 0)),
                nas_account.get('username', formatting.blank()),
                nas_account.get('password', formatting.blank()),
                nas_account.get('serviceResourceBackendIpAddress',
                                formatting.blank())])

        return table
