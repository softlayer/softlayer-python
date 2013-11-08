"""
usage: sl metadata [<command>] [<args>...] [options]

Find details about this machine. These commands only work on devices on the
backend SoftLayer network. This allows for self-discovery for newly provisioned
resources.

The available commands are:
  backend_ip       Primary backend ip address
  backend_mac      Backend mac addresses
  datacenter       Datacenter name
  datacenter_id    Datacenter id
  fqdn             Fully qualified domain name
  frontend_mac     Frontend mac addresses
  hostname         Hostname
  id               Id
  ip               Primary ip address
  network          Details about either the public or private network
  provision_state  Provision state
  tags             Tags
  user_data        User-defined data
"""
# :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
# :license: MIT, see LICENSE for more details.

from SoftLayer import MetadataManager
from SoftLayer.CLI import CLIRunnable, KeyValueTable, listing, CLIAbort


class BackendMacAddresses(CLIRunnable):
    """
usage: sl metadata backend_mac [options]

List backend mac addresses
"""
    action = 'backend_mac'

    def execute(self, args):
        return listing(MetadataManager().get('backend_mac'), separator=',')


class Datacenter(CLIRunnable):
    """
usage: sl metadata datacenter [options]

Get datacenter name
"""
    action = 'datacenter'

    def execute(self, args):
        return MetadataManager().get('datacenter')


class DatacenterId(CLIRunnable):
    """
usage: sl metadata datacenter_id [options]

Get datacenter id
"""
    action = 'datacenter_id'

    def execute(self, args):
        return MetadataManager().get('datacenter_id')


class FrontendMacAddresses(CLIRunnable):
    """
usage: sl metadata frontend_mac [options]

List frontend mac addresses
"""
    action = 'frontend_mac'

    def execute(self, args):
        return listing(MetadataManager().get('frontend_mac'), separator=',')


class FullyQualifiedDomainName(CLIRunnable):
    """
usage: sl metadata fqdn [options]

Get fully qualified domain name
"""
    action = 'fqdn'

    def execute(self, args):
        return MetadataManager().get('fqdn')


class Hostname(CLIRunnable):
    """
usage: sl metadata hostname [options]

Get hostname
"""
    action = 'hostname'

    def execute(self, args):
        return MetadataManager().get('hostname')


class Id(CLIRunnable):
    """
usage: sl metadata id

Get id
"""
    action = 'id'

    def execute(self, args):
        return MetadataManager().get('id')


class PrimaryBackendIpAddress(CLIRunnable):
    """
usage: sl metadata backend_ip [options]

Get primary backend ip address
"""
    action = 'backend_ip'

    def execute(self, args):
        return MetadataManager().get('primary_backend_ip')


class PrimaryIpAddress(CLIRunnable):
    """
usage: sl metadata ip [options]

Get primary ip address
"""
    action = 'ip'

    def execute(self, args):
        return MetadataManager().get('primary_ip')


class ProvisionState(CLIRunnable):
    """
usage: sl metadata provision_state [options]

Get provision state
"""
    action = 'provision_state'

    def execute(self, args):
        return MetadataManager().get('provision_state')


class Tags(CLIRunnable):
    """
usage: sl metadata tags [options]

List tags
"""
    action = 'tags'

    def execute(self, args):
        return listing(MetadataManager().get('tags'), separator=',')


class UserMetadata(CLIRunnable):
    """
usage: sl metadata user_data [options]

Get user-defined data
"""
    action = 'user_data'

    def execute(self, args):
        userdata = MetadataManager().get('user_data')
        if userdata:
            return userdata
        else:
            raise CLIAbort("No user metadata.")


class Network(CLIRunnable):
    """
usage: sl metadata network (<public> | <private>) [options]

Get details about the public or private network
"""
    action = 'network'

    def execute(self, args):
        meta = MetadataManager()
        if args['<public>']:
            t = KeyValueTable(['Name', 'Value'])
            t.align['Name'] = 'r'
            t.align['Value'] = 'l'
            network = meta.public_network()
            t.add_row([
                'mac addresses',
                listing(network['mac_addresses'], separator=',')])
            t.add_row([
                'router', network['router']])
            t.add_row([
                'vlans', listing(network['vlans'], separator=',')])
            t.add_row([
                'vlan ids',
                listing(network['vlan_ids'], separator=',')])
            return t

        if args['<private>']:
            t = KeyValueTable(['Name', 'Value'])
            t.align['Name'] = 'r'
            t.align['Value'] = 'l'
            network = meta.private_network()
            t.add_row([
                'mac addresses',
                listing(network['mac_addresses'], separator=',')])
            t.add_row([
                'router', network['router']])
            t.add_row([
                'vlans', listing(network['vlans'], separator=',')])
            t.add_row([
                'vlan ids',
                listing(network['vlan_ids'], separator=',')])
            return t
