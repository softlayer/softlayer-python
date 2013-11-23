"""
usage: sl subnet [<command>] [<args>...] [options]

Manages subnets on your account.

The available commands are:
  cancel  Cancel a subnet
  create  Create a new subnet
  detail  Display detailed information about a subnet
  list    Show a list of all subnets on the network
  lookup  Find an IP address and display its subnet and device info
"""
# :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
# :license: MIT, see LICENSE for more details.

from SoftLayer import NetworkManager
from SoftLayer.CLI import (
    CLIRunnable, Table, KeyValueTable, FormattedItem, confirm, no_going_back)
from SoftLayer.CLI.helpers import CLIAbort, SequentialOutput


class SubnetCancel(CLIRunnable):
    """
usage: sl subnet cancel <identifier> [options]

Cancel a subnet
"""

    action = 'cancel'
    options = ['confirm']

    def execute(self, args):
        mgr = NetworkManager(self.client)
        subnet_id = mgr.resolve_subnet_ids(args.get('<identifier>'))

        if args['--really'] or no_going_back(subnet_id):
            mgr.cancel_subnet(subnet_id)
        else:
            CLIAbort('Aborted')


class SubnetCreate(CLIRunnable):
    """
usage:
  sl subnet create (public|private) <quantity> <vlan> [options]

Add a new subnet to your account

Required:
  <quantity>           The number of IPs to include in the subnet.
                         Valid quantities vary by type.

                         Type    - Valid Quantities (IPv4)
                         public  - 4, 8, 16, 32
                         private - 4, 8, 16, 32, 64

                         Type    - Valid Quantities (IPv6)
                         public  - 64
  <vlan>               The VLAN ID you want to attach this subnet to

Options:
  --v6                 Orders IPv6
  --dry-run, --test    Do not order the subnet; just get a quote
"""
    action = 'create'
    options = ['confirm']

    def execute(self, args):
        mgr = NetworkManager(self.client)

        _type = 'private'
        if args['public']:
            _type = 'public'

        version = 4
        if args.get('--v6'):
            version = 6
        if not args.get('--test') and not args['--really']:
            if not confirm("This action will incur charges on your account."
                           "Continue?"):
                raise CLIAbort('Cancelling order.')
        result = mgr.add_subnet(_type,
                                quantity=args['<quantity>'],
                                vlan_id=args['<vlan>'],
                                version=version,
                                test_order=args.get('--test'))
        if not result:
            return 'Unable to place order: No valid price IDs found.'
        t = Table(['Item', 'cost'])
        t.align['Item'] = 'r'
        t.align['cost'] = 'r'

        total = 0.0
        for price in result['prices']:
            total += float(price.get('recurringFee', 0.0))
            rate = "%.2f" % float(price['recurringFee'])

            t.add_row([price['item']['description'], rate])

        t.add_row(['Total monthly cost', "%.2f" % total])
        output = SequentialOutput()
        output.append(t)
        output.append(FormattedItem(
            '',
            ' -- ! Prices reflected here are retail and do not '
            'take account level discounts and are not guarenteed.')
        )
        return t


class SubnetDetail(CLIRunnable):
    """
usage: sl subnet detail <identifier> [options]

Get detailed information about objects assigned to a particular subnet

Filters:
  --no-cci         Hide CCI listing
  --no-hardware    Hide hardware listing
"""
    action = 'detail'

    def execute(self, args):
        mgr = NetworkManager(self.client)

        subnet_id = mgr.resolve_subnet_ids(args.get('<identifier>'))
        subnet = mgr.get_subnet(subnet_id)

        t = KeyValueTable(['Name', 'Value'])
        t.align['Name'] = 'r'
        t.align['Value'] = 'l'

        t.add_row(['id', subnet['id']])
        t.add_row(['identifier',
                   subnet['networkIdentifier']+'/'+str(subnet['cidr'])])
        t.add_row(['subnet type', subnet['subnetType']])
        t.add_row(['gateway', subnet.get('gateway', '-')])
        t.add_row(['broadcast', subnet.get('broadcastAddress', '-')])
        t.add_row(['datacenter', subnet['datacenter']['name']])
        t.add_row(['usable ips', subnet.get('usableIpAddressCount', '-')])

        if not args.get('--no-cci'):
            if subnet['virtualGuests']:
                cci_table = Table(['Hostname', 'Domain', 'IP'])
                cci_table.align['Hostname'] = 'r'
                cci_table.align['IP'] = 'l'
                for cci in subnet['virtualGuests']:
                    cci_table.add_row([cci['hostname'],
                                       cci['domain'],
                                       cci.get('primaryIpAddress')])
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
                                      hw.get('primaryIpAddress')])
                t.add_row(['hardware', hw_table])
            else:
                t.add_row(['hardware', 'none'])

        return t


class SubnetList(CLIRunnable):
    """
usage: sl subnet list [options]

Displays a list of subnets

Options:
  --sortby=ARG  Column to sort by. options: id, number, datacenter, IPs,
    hardware, ccis, networking

Filters:
  -d DC, --datacenter=DC   datacenter shortname (sng01, dal05, ...)
  --identifier=ID          Filter by identifier
  -t TYPE, --type=TYPE     Filter by subnet type
  --v4                     Display only IPV4 subnets
  --v6                     Display only IPV6 subnets
"""
    action = 'list'

    def execute(self, args):
        mgr = NetworkManager(self.client)

        t = Table([
            'id', 'identifier', 'type', 'datacenter', 'vlan id', 'IPs',
            'hardware', 'ccis',
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
            identifier=args.get('--identifier'),
            subnet_type=args.get('--type'),
        )

        for subnet in subnets:
            t.add_row([
                subnet['id'],
                subnet['networkIdentifier'] + '/' + str(subnet['cidr']),
                subnet.get('subnetType', '-'),
                subnet['datacenter']['name'],
                subnet['networkVlanId'],
                subnet['ipAddressCount'],
                len(subnet['hardware']),
                len(subnet['virtualGuests']),
            ])

        return t


class SubnetLookup(CLIRunnable):
    """
usage: sl subnet lookup <ip> [options]

Finds an IP address on the network and displays its subnet and device
information.

"""
    action = 'lookup'

    def execute(self, args):
        mgr = NetworkManager(self.client)

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
        subnet_table.add_row(['identifier', ip['subnet']['networkIdentifier']
                              + '/' + str(ip['subnet']['cidr'])])
        subnet_table.add_row(['netmask', ip['subnet']['netmask']])
        if ip['subnet'].get('gateway'):
            subnet_table.add_row(['gateway', ip['subnet']['gateway']])
        subnet_table.add_row(['type', ip['subnet'].get('subnetType')])

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
