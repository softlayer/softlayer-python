"""
usage: sl network [<command>] [<args>...] [options]

Perform various network operations

The available commands are:
  globalip-add     Orders a new global IP address
  globalip-assign  Assign a target to a global IP address
  globalip-cancel  Cancels a global IP
  globalip-list    Display a list of global IP addresses
  ip-lookup        Find information about a specific IP
  rwhois-edit      Edit the RWhois data on the account
  rwhois-show      Show the RWhois data on the account
  subnet-add       Create a new subnet
  subnet-cancel    Cancel a subnet
  subnet-detail    Display detailed information about a subnet
  subnet-list      Show a list of all subnets on the network
  summary          Provide a summary view of the network
  vlan-detail      Display detailed information about a VLAN
  vlan-list        Show a list of all VLANs on the network
"""
# :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
# :license: BSD, see LICENSE for more details.

from SoftLayer import NetworkManager
from SoftLayer.CLI import CLIRunnable, Table, KeyValueTable, FormattedItem, \
    confirm, no_going_back
from SoftLayer.CLI.helpers import CLIAbort, SequentialOutput


class GlobalIpAdd(CLIRunnable):
    """
usage:
  sl network globalip-add [options]

Add a new global IP address to your account.

Options:
  --v6                 Orders IPv6
  --dry-run, --test    Do not order the IP; just get a quote
"""
    action = 'globalip-add'
    options = ['confirm']

    @staticmethod
    def execute(client, args):
        mgr = NetworkManager(client)

        version = 4
        if args.get('--v6'):
            version = 6
        if not args.get('--test') and not args['--really']:
            if not confirm("This action will incur charges on your account."
                           "Continue?"):
                raise CLIAbort('Cancelling order.')
        result = mgr.add_global_ip(version=version,
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


class GlobalIpCancel(CLIRunnable):
    """
usage: sl network globalip-cancel <identifier> [options]

Cancel a subnet
"""

    action = 'subnet-cancel'
    options = ['confirm']

    @staticmethod
    def execute(client, args):
        mgr = NetworkManager(client)
        id = mgr.resolve_global_ip_ids(args.get('<identifier>'))

        if args['--really'] or no_going_back(id):
            mgr.cancel_global_ip(id)
        else:
            CLIAbort('Aborted')


class GlobalIpList(CLIRunnable):
    """
usage: sl network globalip-list [options]

Displays a list of global IPs

Filters:
  --v4                     Display only IPV4
  --v6                     Display only IPV6
"""
    action = 'globalip-list'

    @staticmethod
    def execute(client, args):
        mgr = NetworkManager(client)

        t = Table([
            'id', 'ip', 'assigned', 'target'
        ])
        t.sortby = args.get('--sortby') or 'id'

        version = 0
        if args.get('--v4'):
            version = 4
        elif args.get('--v6'):
            version = 6

        ips = mgr.list_global_ips(version=version)

        for ip in ips:
            assigned = 'No'
            target = 'None'
            if ip.get('destinationIpAddress'):
                dest = ip['destinationIpAddress']
                assigned = 'Yes'
                target = dest['ipAddress']
                if dest.get('virtualGuest'):
                    vg = dest['virtualGuest']
                    target += ' (' + vg['fullyQualifiedDomainName'] + ')'
                elif ip['destinationIpAddress'].get('hardware'):
                    target += ' (' + \
                              dest['hardware']['fullyQualifiedDomainName'] + \
                              ')'

            t.add_row([ip['id'], ip['ipAddress']['ipAddress'], assigned, target])
        return t


class GlobalIpAssign(CLIRunnable):
    """
usage: sl network globalip-assign <identifier> <target> [options]

Assigns a global IP to a target.

Required:
  <identifier>  The ID or address of the global IP
  <target>      The IP address to assign to the global IP
"""
    action = 'globalip-assign'

    @staticmethod
    def execute(client, args):
        mgr = NetworkManager(client)

        id = mgr.resolve_global_ip_ids(args.get('<identifier>'))
        if not id:
            raise CLIAbort("Unable to find global IP record for " +
                           args['<identifier>'])
        mgr.assign_global_ip(id, args['<target>'])


class NetworkLookupIp(CLIRunnable):
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


class RWhoisEdit(CLIRunnable):
    """
usage: sl network rwhois-edit [options]

Updates the RWhois information on your account. Only the fields you
specify will be changed. To clear a value, specify an empty string like: ""

Options:
  --abuse=EMAIL      Set the abuse email
  --address1=ADDR    Update the address 1 field
  --address2=ADDR    Update the address 2 field
  --city=CITY        Set the city information
  --country=COUNTRY  Set the country information. Use the two-letter
                       abbreviation.
  --firstname=NAME   Update the first name field
  --lastname=NAME    Update the last name field
  --postal=CODE      Set the postal code field
  --private          Flags the address as a private residence.
  --public           Flags the address as a public residence.
  --state=STATE      Set the state information. Use the two-letter
                       abbreviation.
"""
    action = 'rwhois-edit'

    @staticmethod
    def execute(client, args):
        mgr = NetworkManager(client)

        update = {
            'abuse_email': args.get('--abuse'),
            'address1': args.get('--address1'),
            'address2': args.get('--address2'),
            'city': args.get('--city'),
            'country': args.get('--country'),
            'first_name': args.get('--firstname'),
            'last_name': args.get('--lastname'),
            'postal_code': args.get('--postal'),
            'state': args.get('--state')
        }

        if args.get('--private'):
            update['private_residence'] = False
        elif args.get('--public'):
            update['private_residence'] = True

        check = [x for x in update.values() if x is not None]
        if not check:
            raise CLIAbort("You must specify at least one field to update.")

        mgr.edit_rwhois(**update)


class RWhoisShow(CLIRunnable):
    """
usage: sl network rwhois-show [options]

Display the RWhois information for your account.
"""
    action = 'rwhois-show'

    @staticmethod
    def execute(client, args):
        mgr = NetworkManager(client)
        result = mgr.get_rwhois()

        t = KeyValueTable(['Name', 'Value'])
        t.align['Name'] = 'r'
        t.align['Value'] = 'l'
        t.add_row(['Name', result['firstName'] + ' ' + result['lastName']])
        t.add_row(['Company', result['companyName']])
        t.add_row(['Abuse Email', result['abuseEmail']])
        t.add_row(['Address 1', result['address1']])
        if result.get('address2'):
            t.add_row(['Address 2', result['address2']])
        t.add_row(['City', result['city']])
        t.add_row(['State', result.get('state', '-')])
        t.add_row(['Postal Code', result.get('postalCode', '-')])
        t.add_row(['Country', result['country']])

        return t


class SubnetAdd(CLIRunnable):
    """
usage:
  sl network subnet-add (public|private) <quantity> <vlan> [options]

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
    action = 'subnet-add'
    options = ['confirm']

    @staticmethod
    def execute(client, args):
        mgr = NetworkManager(client)

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
        result = mgr.add_subnet(type=_type,
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


class SubnetCancel(CLIRunnable):
    """
usage: sl network subnet-cancel <identifier> [options]

Cancel a subnet
"""

    action = 'subnet-cancel'
    options = ['confirm']

    @staticmethod
    def execute(client, args):
        mgr = NetworkManager(client)
        subnet_id = mgr.resolve_subnet_ids(args.get('<identifier>'))

        if args['--really'] or no_going_back(subnet_id):
            mgr.cancel_subnet(subnet_id)
        else:
            CLIAbort('Aborted')


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

        subnet_id = mgr.resolve_subnet_ids(args.get('<identifier>'))
        subnet = mgr.get_subnet(subnet_id)

        t = KeyValueTable(['Name', 'Value'])
        t.align['Name'] = 'r'
        t.align['Value'] = 'l'

        t.add_row(['id', subnet['id']])
        t.add_row(['identifier', subnet['networkIdentifier']])
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
usage: sl network subnet-list [options]

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
    action = 'subnet-list'

    @staticmethod
    def execute(client, args):
        mgr = NetworkManager(client)

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
                subnet['networkIdentifier'],
                subnet.get('subnetType', '-'),
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
