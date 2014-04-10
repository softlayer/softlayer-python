"""
usage: sl summary [options]

Display summary information about the account
"""
# :license: MIT, see LICENSE for more details.

from SoftLayer import NetworkManager
from SoftLayer.CLI import CLIRunnable, Table


class Summary(CLIRunnable):
    """
usage: sl summary [options]

Display summary information about the account

Options:
  --sortby=ARG  Column to sort by. options: datacenter, vlans,
                subnets, IPs, networking, hardware, vs
"""
    action = None

    def execute(self, args):
        mgr = NetworkManager(self.client)
        datacenters = mgr.summary_by_datacenter()

        table = Table([
            'datacenter', 'vlans', 'subnets', 'IPs', 'networking',
            'hardware', 'vs'
        ])
        table.sortby = args.get('--sortby') or 'datacenter'

        for name, datacenter in datacenters.items():
            table.add_row([
                name,
                datacenter['vlanCount'],
                datacenter['subnetCount'],
                datacenter['primaryIpCount'],
                datacenter['networkingCount'],
                datacenter['hardwareCount'],
                datacenter['virtualGuestCount'],
            ])

        return table
