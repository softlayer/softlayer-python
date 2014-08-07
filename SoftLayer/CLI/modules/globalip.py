"""
usage: sl globalip [<command>] [<args>...] [options]

Orders or configures global IP addresses

The available commands are:
  assign    Assign a target to a global IP address
  cancel    Cancels a global IP
  create    Orders a new global IP address
  list      Display a list of global IP addresses
  unassign  Unassigns a global IP
"""
# :license: MIT, see LICENSE for more details.

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers


class GlobalIpAssign(environment.CLIRunnable):
    """
usage: sl globalip assign <identifier> <target> [options]

Assigns a global IP to a target.

Required:
  <identifier>  The ID or address of the global IP
  <target>      The IP address to assign to the global IP
"""
    action = 'assign'

    def execute(self, args):
        mgr = SoftLayer.NetworkManager(self.client)
        global_ip_id = helpers.resolve_id(mgr.resolve_global_ip_ids,
                                          args.get('<identifier>'),
                                          name='global ip')
        mgr.assign_global_ip(global_ip_id, args['<target>'])


class GlobalIpCancel(environment.CLIRunnable):
    """
usage: sl globalip cancel <identifier> [options]

Cancel a subnet
"""

    action = 'cancel'
    options = ['confirm']

    def execute(self, args):
        mgr = SoftLayer.NetworkManager(self.client)
        global_ip_id = helpers.resolve_id(mgr.resolve_global_ip_ids,
                                          args.get('<identifier>'),
                                          name='global ip')

        if args['--really'] or formatting.no_going_back(global_ip_id):
            mgr.cancel_global_ip(global_ip_id)
        else:
            raise exceptions.CLIAbort('Aborted')


class GlobalIpCreate(environment.CLIRunnable):
    """
usage:
  sl globalip create [options]

Add a new global IP address to your account.

Options:
  --v6                 Orders IPv6
  --test               Do not order the IP; just get a quote
"""
    action = 'create'
    options = ['confirm']

    def execute(self, args):
        mgr = SoftLayer.NetworkManager(self.client)

        version = 4
        if args.get('--v6'):
            version = 6
        if not args.get('--test') and not args['--really']:
            if not formatting.confirm("This action will incur charges on your "
                                      "account. Continue?"):
                raise exceptions.CLIAbort('Cancelling order.')
        result = mgr.add_global_ip(version=version,
                                   test_order=args.get('--test'))

        table = formatting.Table(['Item', 'cost'])
        table.align['Item'] = 'r'
        table.align['cost'] = 'r'

        total = 0.0
        for price in result['orderDetails']['prices']:
            total += float(price.get('recurringFee', 0.0))
            rate = "%.2f" % float(price['recurringFee'])

            table.add_row([price['item']['description'], rate])

        table.add_row(['Total monthly cost', "%.2f" % total])
        return table


class GlobalIpList(environment.CLIRunnable):
    """
usage: sl globalip list [options]

Displays a list of global IPs

Filters:
  --v4                     Display only IPV4
  --v6                     Display only IPV6
"""
    action = 'list'

    def execute(self, args):
        mgr = SoftLayer.NetworkManager(self.client)

        table = formatting.Table(['id', 'ip', 'assigned', 'target'])
        table.sortby = args.get('--sortby') or 'id'

        version = 0
        if args.get('--v4'):
            version = 4
        elif args.get('--v6'):
            version = 6

        ips = mgr.list_global_ips(version=version)

        for ip_address in ips:
            assigned = 'No'
            target = 'None'
            if ip_address.get('destinationIpAddress'):
                dest = ip_address['destinationIpAddress']
                assigned = 'Yes'
                target = dest['ipAddress']
                virtual_guest = dest.get('virtualGuest')
                if virtual_guest:
                    target += (' (%s)'
                               % virtual_guest['fullyQualifiedDomainName'])
                elif ip_address['destinationIpAddress'].get('hardware'):
                    target += (' (%s)'
                               % dest['hardware']['fullyQualifiedDomainName'])

            table.add_row([ip_address['id'],
                           ip_address['ipAddress']['ipAddress'],
                           assigned,
                           target])
        return table


class GlobalIpUnassign(environment.CLIRunnable):
    """
usage: sl globalip unassign <identifier> [options]

Unassigns a global IP from a target.

Required:
  <identifier>  The ID or address of the global IP
"""
    action = 'unassign'

    def execute(self, args):
        mgr = SoftLayer.NetworkManager(self.client)
        global_ip_id = helpers.resolve_id(mgr.resolve_global_ip_ids,
                                          args.get('<identifier>'),
                                          name='global ip')
        mgr.unassign_global_ip(global_ip_id)
