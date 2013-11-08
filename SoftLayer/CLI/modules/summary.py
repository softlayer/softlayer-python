"""
usage: sl summary [options]

Display summary information about the account
"""
# :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
# :license: MIT, see LICENSE for more details.

from SoftLayer import NetworkManager
from SoftLayer.CLI import CLIRunnable, Table


class Summary(CLIRunnable):
    """
usage: sl summary [options]

Display summary information about the account

Options:
  --sortby=ARG  Column to sort by. options: datacenter, vlans,
                subnets, IPs, networking, hardware, ccis, firewall
"""
    action = None

    def execute(self, args):
        mgr = NetworkManager(self.client)
        datacenters = mgr.summary_by_datacenter()

        t = Table([
            'datacenter', 'vlans', 'subnets', 'IPs', 'networking',
            'hardware', 'ccis'
        ])
        t.sortby = args.get('--sortby') or 'datacenter'

        for name, dc in datacenters.iteritems():
            t.add_row([
                name,
                dc['vlanCount'],
                dc['subnetCount'],
                dc['primaryIpCount'],
                dc['networkingCount'],
                dc['hardwareCount'],
                dc['virtualGuestCount'],
            ])

        return t
