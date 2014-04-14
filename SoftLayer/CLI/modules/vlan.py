"""
usage: sl vlan [<command>] [<args>...] [options]

Display information about VLANs on the network

The available commands are:
  detail  Display detailed information about a VLAN
  list    Show a list of all VLANs on the network
"""
# :license: MIT, see LICENSE for more details.

from SoftLayer import NetworkManager
from SoftLayer.CLI import CLIRunnable, Table, KeyValueTable, blank, resolve_id


class VlanDetail(CLIRunnable):
    """
usage: sl vlan detail <identifier> [options]

Get detailed information about objects assigned to a particular VLAN

Filters:
  --no-vs, --no-cci  Hide virtual server listing
  --no-hardware      Hide hardware listing
"""
    action = 'detail'

    def execute(self, args):
        mgr = NetworkManager(self.client)

        vlan_id = resolve_id(mgr.resolve_vlan_ids,
                             args.get('<identifier>'),
                             'VLAN')
        vlan = mgr.get_vlan(vlan_id)

        table = KeyValueTable(['Name', 'Value'])
        table.align['Name'] = 'r'
        table.align['Value'] = 'l'

        table.add_row(['id', vlan['id']])
        table.add_row(['number', vlan['vlanNumber']])
        table.add_row(['datacenter',
                       vlan['primaryRouter']['datacenter']['longName']])
        table.add_row(['primary router',
                       vlan['primaryRouter']['fullyQualifiedDomainName']])
        table.add_row(['firewall',
                       'Yes' if vlan['firewallInterfaces'] else 'No'])
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

        table.add_row(['subnets', subnets])

        if not args.get('--no-vs'):
            if vlan['virtualGuests']:
                vs_table = KeyValueTable(['Hostname', 'Domain', 'IP'])
                vs_table.align['Hostname'] = 'r'
                vs_table.align['IP'] = 'l'
                for vsi in vlan['virtualGuests']:
                    vs_table.add_row([vsi['hostname'],
                                      vsi['domain'],
                                      vsi.get('primaryIpAddress')])
                table.add_row(['vs', vs_table])
            else:
                table.add_row(['vs', 'none'])

        if not args.get('--no-hardware'):
            if vlan['hardware']:
                hw_table = Table(['Hostname', 'Domain', 'IP'])
                hw_table.align['Hostname'] = 'r'
                hw_table.align['IP'] = 'l'
                for hardware in vlan['hardware']:
                    hw_table.add_row([hardware['hostname'],
                                      hardware['domain'],
                                      hardware.get('primaryIpAddress')])
                table.add_row(['hardware', hw_table])
            else:
                table.add_row(['hardware', 'none'])

        return table


class VlanList(CLIRunnable):
    """
usage: sl vlan list [options]

Displays a list of VLANs

Options:
  --sortby=ARG  Column to sort by. options: id, number, datacenter, IPs,
    hardware, vs, networking

Filters:
  -d DC, --datacenter=DC  datacenter shortname (sng01, dal05, ...)
  -n NUM, --number=NUM    VLAN number
  --name=NAME             VLAN name
"""
    action = 'list'

    def execute(self, args):
        mgr = NetworkManager(self.client)

        table = Table([
            'id', 'number', 'datacenter', 'name', 'IPs', 'hardware', 'vs',
            'networking', 'firewall'
        ])
        table.sortby = args.get('--sortby') or 'id'

        vlans = mgr.list_vlans(
            datacenter=args.get('--datacenter'),
            vlan_number=args.get('--number'),
            name=args.get('--name'),
        )
        for vlan in vlans:
            table.add_row([
                vlan['id'],
                vlan['vlanNumber'],
                vlan['primaryRouter']['datacenter']['name'],
                vlan.get('name') or blank(),
                vlan['totalPrimaryIpAddressCount'],
                len(vlan['hardware']),
                len(vlan['virtualGuests']),
                len(vlan['networkComponents']),
                'Yes' if vlan['firewallInterfaces'] else 'No',
            ])

        return table
