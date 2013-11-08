"""
usage: sl vlan [<command>] [<args>...] [options]

Display information about VLANs on the network

The available commands are:
  detail  Display detailed information about a VLAN
  list    Show a list of all VLANs on the network
"""
# :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
# :license: MIT, see LICENSE for more details.

from SoftLayer import NetworkManager
from SoftLayer.CLI import CLIRunnable, Table, KeyValueTable


class VlanDetail(CLIRunnable):
    """
usage: sl vlan detail <identifier> [options]

Get detailed information about objects assigned to a particular VLAN

Filters:
  --no-cci         Hide CCI listing
  --no-hardware    Hide hardware listing
"""
    action = 'detail'

    def execute(self, args):
        mgr = NetworkManager(self.client)

        vlan = mgr.get_vlan(args.get('<identifier>'))

        t = KeyValueTable(['Name', 'Value'])
        t.align['Name'] = 'r'
        t.align['Value'] = 'l'

        t.add_row(['id', vlan['id']])
        t.add_row(['number', vlan['vlanNumber']])
        t.add_row(['datacenter',
                   vlan['primaryRouter']['datacenter']['longName']])
        t.add_row(['primary router',
                   vlan['primaryRouter']['fullyQualifiedDomainName']])
        t.add_row(['firewall', 'Yes' if vlan['firewallInterfaces'] else 'No'])
        subnets = []
        for subnet in vlan['subnets']:
            subnet_table = KeyValueTable(['Name', 'Value'])
            subnet_table.align['Name'] = 'r'
            subnet_table.align['Value'] = 'l'
            subnet_table.add_row(['id', subnet['id']])
            subnet_table.add_row(['identifier', subnet['networkIdentifier']])
            subnet_table.add_row(['netmask', subnet['netmask']])
            subnet_table.add_row(['gateway', subnet.get('gateway', '-')])
            subnet_table.add_row(['type', subnet['subnetType']])
            subnet_table.add_row(['usable ips',
                                  subnet['usableIpAddressCount']])
            subnets.append(subnet_table)

        t.add_row(['subnets', subnets])

        if not args.get('--no-cci'):
            if vlan['virtualGuests']:
                cci_table = KeyValueTable(['Hostname', 'Domain', 'IP'])
                cci_table.align['Hostname'] = 'r'
                cci_table.align['IP'] = 'l'
                for cci in vlan['virtualGuests']:
                    cci_table.add_row([cci['hostname'],
                                       cci['domain'],
                                       cci.get('primaryIpAddress')])
                t.add_row(['ccis', cci_table])
            else:
                t.add_row(['cci', 'none'])

        if not args.get('--no-hardware'):
            if vlan['hardware']:
                hw_table = Table(['Hostname', 'Domain', 'IP'])
                hw_table.align['Hostname'] = 'r'
                hw_table.align['IP'] = 'l'
                for hw in vlan['hardware']:
                    hw_table.add_row([hw['hostname'],
                                      hw['domain'],
                                      hw.get('primaryIpAddress')])
                t.add_row(['hardware', hw_table])
            else:
                t.add_row(['hardware', 'none'])

        return t


class VlanList(CLIRunnable):
    """
usage: sl vlan list [options]

Displays a list of VLANs

Options:
  --sortby=ARG  Column to sort by. options: id, number, datacenter, IPs,
    hardware, ccis, networking

Filters:
  -d DC, --datacenter=DC   datacenter shortname (sng01, dal05, ...)
  -n NUM, --number=NUM     VLAN number
"""
    action = 'list'

    def execute(self, args):
        mgr = NetworkManager(self.client)

        t = Table([
            'id', 'number', 'datacenter', 'IPs', 'hardware', 'ccis',
            'networking', 'firewall'
        ])
        t.sortby = args.get('--sortby') or 'id'

        vlans = mgr.list_vlans(
            datacenter=args.get('--datacenter'),
            vlan_number=args.get('--number')
        )
        for vlan in vlans:
            t.add_row([
                vlan['id'],
                vlan['vlanNumber'],
                vlan['primaryRouter']['datacenter']['name'],
                vlan['totalPrimaryIpAddressCount'],
                len(vlan['hardware']),
                len(vlan['virtualGuests']),
                len(vlan['networkComponents']),
                'Yes' if vlan['firewallInterfaces'] else 'No',
            ])

        return t
