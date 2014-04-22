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
# :license: MIT, see LICENSE for more details.

from SoftLayer import NetworkManager
from SoftLayer.utils import lookup
from SoftLayer.CLI import (
    CLIRunnable, Table, KeyValueTable, confirm, no_going_back, resolve_id)
from SoftLayer.CLI.helpers import CLIAbort, blank


class SubnetCancel(CLIRunnable):
    """
usage: sl subnet cancel <identifier> [options]

Cancel a subnet
"""

    action = 'cancel'
    options = ['confirm']

    def execute(self, args):
        mgr = NetworkManager(self.client)
        subnet_id = resolve_id(mgr.resolve_subnet_ids,
                               args.get('<identifier>'),
                               name='subnet')

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
        table = Table(['Item', 'cost'])
        table.align['Item'] = 'r'
        table.align['cost'] = 'r'

        total = 0.0
        if 'prices' in result:
            for price in result['prices']:
                total += float(price.get('recurringFee', 0.0))
                rate = "%.2f" % float(price['recurringFee'])

                table.add_row([price['item']['description'], rate])

        table.add_row(['Total monthly cost', "%.2f" % total])
        return table


class SubnetDetail(CLIRunnable):
    """
usage: sl subnet detail <identifier> [options]

Get detailed information about objects assigned to a particular subnet

Filters:
  --no-vs, --no-cci  Hide virtual server listing
  --no-hardware      Hide hardware listing
"""
    action = 'detail'

    def execute(self, args):
        mgr = NetworkManager(self.client)
        subnet_id = resolve_id(mgr.resolve_subnet_ids,
                               args.get('<identifier>'),
                               name='subnet')
        subnet = mgr.get_subnet(subnet_id)

        table = KeyValueTable(['Name', 'Value'])
        table.align['Name'] = 'r'
        table.align['Value'] = 'l'

        table.add_row(['id', subnet['id']])
        table.add_row(['identifier',
                       '%s/%s' % (subnet['networkIdentifier'],
                                  str(subnet['cidr']))])
        table.add_row(['subnet type', subnet['subnetType']])
        table.add_row(['gateway', subnet.get('gateway', blank())])
        table.add_row(['broadcast', subnet.get('broadcastAddress', blank())])
        table.add_row(['datacenter', subnet['datacenter']['name']])
        table.add_row(['usable ips',
                       subnet.get('usableIpAddressCount', blank())])

        if not args.get('--no-vs'):
            if subnet['virtualGuests']:
                vs_table = Table(['Hostname', 'Domain', 'IP'])
                vs_table.align['Hostname'] = 'r'
                vs_table.align['IP'] = 'l'
                for vsi in subnet['virtualGuests']:
                    vs_table.add_row([vsi['hostname'],
                                      vsi['domain'],
                                      vsi.get('primaryIpAddress')])
                table.add_row(['vs', vs_table])
            else:
                table.add_row(['vs', 'none'])

        if not args.get('--no-hardware'):
            if subnet['hardware']:
                hw_table = Table(['Hostname', 'Domain', 'IP'])
                hw_table.align['Hostname'] = 'r'
                hw_table.align['IP'] = 'l'
                for hardware in subnet['hardware']:
                    hw_table.add_row([hardware['hostname'],
                                      hardware['domain'],
                                      hardware.get('primaryIpAddress')])
                table.add_row(['hardware', hw_table])
            else:
                table.add_row(['hardware', 'none'])

        return table


class SubnetList(CLIRunnable):
    """
usage: sl subnet list [options]

Displays a list of subnets

Options:
  --sortby=ARG  Column to sort by. options: id, identifier, type, datacenter,
    vlan id, IPs, hardware, vs

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

        table = Table([
            'id', 'identifier', 'type', 'datacenter', 'vlan id', 'IPs',
            'hardware', 'vs',
        ])
        table.sortby = args.get('--sortby') or 'id'

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
            table.add_row([
                subnet['id'],
                '%s/%s' % (subnet['networkIdentifier'], str(subnet['cidr'])),
                subnet.get('subnetType', blank()),
                lookup(subnet, 'datacenter', 'name',) or blank(),
                subnet['networkVlanId'],
                subnet['ipAddressCount'],
                len(subnet['hardware']),
                len(subnet['virtualGuests']),
            ])

        return table


class SubnetLookup(CLIRunnable):
    """
usage: sl subnet lookup <ip> [options]

Finds an IP address on the network and displays its subnet and device
information.

"""
    action = 'lookup'

    def execute(self, args):
        mgr = NetworkManager(self.client)

        addr_info = mgr.ip_lookup(args['<ip>'])

        if not addr_info:
            return 'Not found'

        table = KeyValueTable(['Name', 'Value'])
        table.align['Name'] = 'r'
        table.align['Value'] = 'l'

        table.add_row(['id', addr_info['id']])
        table.add_row(['ip', addr_info['ipAddress']])

        subnet_table = KeyValueTable(['Name', 'Value'])
        subnet_table.align['Name'] = 'r'
        subnet_table.align['Value'] = 'l'
        subnet_table.add_row(['id', addr_info['subnet']['id']])
        subnet_table.add_row(['identifier',
                              '%s/%s'
                              % (addr_info['subnet']['networkIdentifier'],
                                 str(addr_info['subnet']['cidr']))])
        subnet_table.add_row(['netmask', addr_info['subnet']['netmask']])
        if addr_info['subnet'].get('gateway'):
            subnet_table.add_row(['gateway', addr_info['subnet']['gateway']])
        subnet_table.add_row(['type', addr_info['subnet'].get('subnetType')])

        table.add_row(['subnet', subnet_table])

        if addr_info.get('virtualGuest') or addr_info.get('hardware'):
            device_table = KeyValueTable(['Name', 'Value'])
            device_table.align['Name'] = 'r'
            device_table.align['Value'] = 'l'
            if addr_info.get('virtualGuest'):
                device = addr_info['virtualGuest']
                device_type = 'vs'
            else:
                device = addr_info['hardware']
                device_type = 'server'
            device_table.add_row(['id', device['id']])
            device_table.add_row(['name', device['fullyQualifiedDomainName']])
            device_table.add_row(['type', device_type])
            table.add_row(['device', device_table])
        return table
