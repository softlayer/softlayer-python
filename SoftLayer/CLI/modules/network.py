"""
usage: sl network [<command>] [<args>...] [options]

Perform various network operations

The available commands are:
  ip-lookup       Find information about a specific IP
  summary         Provide a summary view of the network
  subnet-detail   Display detailed information about a subnet
  subnet-list     Show a list of all subnets on the network
  vlan-detail     Display detailed information about a VLAN
  vlan-list       Show a list of all VLANs on the network
"""
# Removed the following line due to an API bug:
#   subnet-add      Create a new subnet
# :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
# :license: BSD, see LICENSE for more details.

from SoftLayer import NetworkManager
from SoftLayer.CLI import (CLIRunnable, Table, KeyValueTable, FormattedItem,
                           confirm)
from SoftLayer.CLI.helpers import (CLIAbort, SequentialOutput)


class NetworkFindIp(CLIRunnable):
    """
usage: sl network ip-lookup <ip>

Finds an IP address on the network and displays its subnet and VLAN
information.

"""
    action = 'ip-lookup'

    @staticmethod
    def execute(client, args):
        mgr = NetworkManager(client)

        ip = mgr.ip_lookup(args['<ip>'])

        if not ip:
            return 'Not found'

        t = KeyValueTable(['Name', 'Value'])
        t.align['Name'] = 'r'
        t.align['Value'] = 'l'

        t.add_row(['id', ip['id']])
        t.add_row(['ip', ip['ipAddress']])

        subnet_table = KeyValueTable(['Name', 'Value'])
        subnet_table.align['Name'] = 'r'
        subnet_table.align['Value'] = 'l'
        subnet_table.add_row(['id', ip['subnet']['id']])
        subnet_table.add_row(['identifier', ip['subnet']['networkIdentifier']])
        subnet_table.add_row(['netmask', ip['subnet']['netmask']])
        if ip['subnet'].get('gateway'):
            subnet_table.add_row(['gateway', ip['subnet']['gateway']])
        subnet_table.add_row(['type', ip['subnet']['subnetType']])

        t.add_row(['subnet', subnet_table])

        if ip.get('virtualGuest') or ip.get('hardware'):
            device_table = KeyValueTable(['Name', 'Value'])
            device_table.align['Name'] = 'r'
            device_table.align['Value'] = 'l'
            if ip.get('virtualGuest'):
                device = ip['virtualGuest']
                device_type = 'cci'
            else:
                device = ip['hardware']
                device_type = 'server'
            device_table.add_row(['id', device['id']])
            device_table.add_row(['name', device['fullyQualifiedDomainName']])
            device_table.add_row(['type', device_type])
            t.add_row(['device', device_table])
        return t


class NetworkSummary(CLIRunnable):
    """
usage: sl network summary [options]

Display a network summary

Options:
  --sortby=ARG  Column to sort by. options: datacenter, vlans,
                subnets, IPs, networking, hardware, ccis, firewall
"""
    action = 'summary'

    @staticmethod
    def execute(client, args):
        mgr = NetworkManager(client)
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


# Temporarily removing this due to an API bug not allowing subnet ordering
# class SubnetAdd(CLIRunnable):
#     """
# usage:
#   sl network subnet-add (public|private) <quantity> <vlan> [options]
#   sl network subnet-add global [options]

# Add a new subnet to your account

# Required:
#   <quantity>           The number of IPs to include in the subnet.
#                          Valid quantities vary by type.

#                          Type    - Valid Quantities (IPv4)
#                          global  - 1
#                          public  - 4, 8, 16, 32
#                          private - 4, 8, 16, 32, 64

#                          Type    - Valid Quantities (IPv6)
#                          global  - 1
#                          public  - 64
#   <vlan>               The VLAN ID you want to attach this subnet to

# Options:
#   --v6                 Orders IPv6
#   --dry-run, --test    Do not order the subnet; just get a quote
# """
#     action = 'subnet-add'
#     options = ['confirm']

#     @staticmethod
#     def execute(client, args):
#         mgr = NetworkManager(client)

#         _type = 'private'
#         if args['public']:
#             _type = 'public'
#         elif args['global']:
#             _type = 'global'

#         version = 4
#         if args.get('--v6'):
#             version = 6
#         if not args.get('--test') and not args['--really']:
#             if not confirm("This action will incur charges on your account."
#                            "Continue?"):
#                 raise CLIAbort('Cancelling order.')
#         result = mgr.add_subnet(type=_type,
#                                 quantity=args['<quantity>'],
#                                 vlan_id=args['<vlan>'],
#                                 version=version,
#                                 test_order=args.get('--test'))
#         if not result:
#             return 'Unable to place order: No valid price IDs found.'
#         t = Table(['Item', 'cost'])
#         t.align['Item'] = 'r'
#         t.align['cost'] = 'r'

#         total = 0.0
#         for price in result['prices']:
#             total += float(price.get('recurringFee', 0.0))
#             rate = "%.2f" % float(price['recurringFee'])

#             t.add_row([price['item']['description'], rate])

#         t.add_row(['Total monthly cost', "%.2f" % total])
#         output = SequentialOutput()
#         output.append(t)
#         output.append(FormattedItem(
#             '',
#             ' -- ! Prices reflected here are retail and do not '
#             'take account level discounts and are not guarenteed.')
#         )
#         return t


class SubnetDetail(CLIRunnable):
    """
usage: sl network subnet-detail <identifier> [options]

Get detailed information about objects assigned to a particular subnet

Filters:
  --no-cci         Hide CCI listing
  --no-hardware    Hide hardware listing
"""
    action = 'subnet-detail'

    @staticmethod
    def execute(client, args):
        mgr = NetworkManager(client)

        subnet = mgr.get_subnet(args.get('<identifier>'))

        t = KeyValueTable(['Name', 'Value'])
        t.align['Name'] = 'r'
        t.align['Value'] = 'l'

        t.add_row(['id', subnet['id']])
        t.add_row(['identifier', subnet['networkIdentifier']])
        t.add_row(['subnet type', subnet['subnetType']])
        t.add_row(['gateway', subnet['gateway']])
        t.add_row(['broadcast', subnet['broadcastAddress']])
        t.add_row(['datacenter', subnet['datacenter']['name']])
        t.add_row(['usable ips', subnet['usableIpAddressCount']])

        if not args.get('--no-cci'):
            if subnet['virtualGuests']:
                cci_table = Table(['Hostname', 'Domain', 'IP'])
                cci_table.align['Hostname'] = 'r'
                cci_table.align['IP'] = 'l'
                for cci in subnet['virtualGuests']:
                    cci_table.add_row([cci['hostname'],
                                       cci['domain'],
                                       cci['primaryIpAddress']])
                t.add_row(['ccis', cci_table])
            else:
                t.add_row(['cci', 'none'])

        if not args.get('--no-hardware'):
            if subnet['hardware']:
                hw_table = Table(['Hostname', 'Domain', 'IP'])
                hw_table.align['Hostname'] = 'r'
                hw_table.align['IP'] = 'l'
                for hw in subnet['hardware']:
                    hw_table.add_row([hw['hostname'],
                                      hw['domain'],
                                      hw['primaryIpAddress']])
                t.add_row(['hardware', hw_table])
            else:
                t.add_row(['hardware', 'none'])

        return t


class SubnetList(CLIRunnable):
    """
usage: sl network subnet-list [options]

Displays a list of subnets

Options:
  --sortby=ARG  Column to sort by. options: id, number, datacenter, IPs,
    hardware, ccis, networking

Filters:
  -d DC, --datacenter=DC   datacenter shortname (sng01, dal05, ...)
  --v4                     Display only IPV4 subnets
  --v6                     Display only IPV6 subnets
"""
    action = 'subnet-list'

    @staticmethod
    def execute(client, args):
        mgr = NetworkManager(client)

        t = Table([
            'id', 'identifier', 'datacenter', 'vlan id', 'IPs', 'hardware',
            'ccis',
        ])
        t.sortby = args.get('--sortby') or 'id'

        version = 0
        if args.get('--v4'):
            version = 4
        elif args.get('--v6'):
            version = 6

        subnets = mgr.list_subnets(
            datacenter=args.get('--datacenter'),
            version=version,
        )

        for subnet in subnets:
            t.add_row([
                subnet['id'],
                subnet['networkIdentifier'],
                subnet['datacenter']['name'],
                subnet['networkVlanId'],
                subnet['ipAddressCount'],
                len(subnet['hardware']),
                len(subnet['virtualGuests']),
            ])

        return t


class VlanDetail(CLIRunnable):
    """
usage: sl network vlan-detail <identifier> [options]

Get detailed information about objects assigned to a particular VLAN

Filters:
  --no-cci         Hide CCI listing
  --no-hardware    Hide hardware listing
"""
    action = 'vlan-detail'

    @staticmethod
    def execute(client, args):
        mgr = NetworkManager(client)

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
            subnet_table.add_row(['gateway', subnet['gateway']])
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
                                       cci['primaryIpAddress']])
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
                                      hw['primaryIpAddress']])
                t.add_row(['hardware', hw_table])
            else:
                t.add_row(['hardware', 'none'])

        return t


class VlanList(CLIRunnable):
    """
usage: sl network vlan-list [options]

Displays a list of VLANs

Options:
  --sortby=ARG  Column to sort by. options: id, number, datacenter, IPs,
    hardware, ccis, networking

Filters:
  -d DC, --datacenter=DC   datacenter shortname (sng01, dal05, ...)
  -n NUM, --number=NUM     VLAN number
"""
    action = 'vlan-list'

    @staticmethod
    def execute(client, args):
        mgr = NetworkManager(client)

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
