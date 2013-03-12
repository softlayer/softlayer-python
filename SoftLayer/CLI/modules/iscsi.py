"""
usage: sl iscsi [<command>] [<args>...] [options]

Manage iSCSI targets

The available commands are:
  list  List NAS accounts
"""

from SoftLayer.CLI import CLIRunnable, Table, FormattedItem
from SoftLayer.CLI.helpers import NestedDict


class ListISCSI(CLIRunnable):
    """
usage: sl iscsi list [options]

List iSCSI accounts

Options:
"""
    action = 'list'

    @staticmethod
    def execute(client, args):
        account = client['Account']

        iscsi = account.getIscsiNetworkStorage(
            mask='eventCount,serviceResource[datacenter.name]')
        iscsi = [NestedDict(n) for n in iscsi]

        t = Table(['id', 'datacenter', 'size', 'username',
            'password', 'server'])

        for n in iscsi:
            t.add_row([
                n['id'],
                n['serviceResource']['datacenter'].get('name', '-'),
                FormattedItem(n.get('capacityGb', '-'),
                    "%dGB" % n.get('capacityGb', 0)),
                n.get('username', '-'),
                n.get('password', '-'),
                n.get('serviceResourceBackendIpAddress', '-')])

        return t
