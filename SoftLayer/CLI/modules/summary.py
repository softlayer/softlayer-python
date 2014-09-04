"""
usage: sl summary [<command>] [<args>...] [options]

Display summary information about the account

Options:
  --sortby=ARG  Column to sort by. options: datacenter, vlans,
                subnets, IPs, networking, hardware, vs
"""
# :license: MIT, see LICENSE for more details.
# pylint: disable=missing-docstring

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting


class Summary(environment.CLIRunnable):
    __doc__ = __doc__
    action = None

    def execute(self, args):
        mgr = SoftLayer.NetworkManager(self.client)
        datacenters = mgr.summary_by_datacenter()

        table = formatting.Table([
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
