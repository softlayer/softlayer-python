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
# :license: MIT, see LICENSE for more details.

from SoftLayer import MetadataManager, TransportError
from SoftLayer.CLI import CLIRunnable, KeyValueTable, listing, CLIAbort


class MetaRunnable(CLIRunnable):
    """ A CLIRunnable that raises a nice error on connection issues because
        the metadata service is only accessable on a SoftLayer device """
    def execute(self, args):
        try:
            return self._execute(args)
        except TransportError:
            raise CLIAbort(
                'Cannot connect to the backend service address. Make sure '
                'this command is being ran from a device on the backend '
                'network.')

    def _execute(self, _):
        """ To be overridden exactly like the execute() method """
        pass


class BackendMacAddresses(MetaRunnable):
    """
usage: sl metadata backend_mac [options]

List backend mac addresses
"""
    action = 'backend_mac'

    def _execute(self, _):
        return listing(MetadataManager().get('backend_mac'), separator=',')


class Datacenter(MetaRunnable):
    """
usage: sl metadata datacenter [options]

Get datacenter name
"""
    action = 'datacenter'

    def _execute(self, _):
        return MetadataManager().get('datacenter')


class DatacenterId(MetaRunnable):
    """
usage: sl metadata datacenter_id [options]

Get datacenter id
"""
    action = 'datacenter_id'

    def _execute(self, _):
        return MetadataManager().get('datacenter_id')


class FrontendMacAddresses(MetaRunnable):
    """
usage: sl metadata frontend_mac [options]

List frontend mac addresses
"""
    action = 'frontend_mac'

    def _execute(self, _):
        return listing(MetadataManager().get('frontend_mac'), separator=',')


class FullyQualifiedDomainName(MetaRunnable):
    """
usage: sl metadata fqdn [options]

Get fully qualified domain name
"""
    action = 'fqdn'

    def _execute(self, _):
        return MetadataManager().get('fqdn')


class Hostname(MetaRunnable):
    """
usage: sl metadata hostname [options]

Get hostname
"""
    action = 'hostname'

    def _execute(self, _):
        return MetadataManager().get('hostname')


class Id(MetaRunnable):
    """
usage: sl metadata id

Get id
"""
    action = 'id'

    def _execute(self, _):
        return MetadataManager().get('id')


class PrimaryBackendIpAddress(MetaRunnable):
    """
usage: sl metadata backend_ip [options]

Get primary backend ip address
"""
    action = 'backend_ip'

    def _execute(self, _):
        return MetadataManager().get('primary_backend_ip')


class PrimaryIpAddress(MetaRunnable):
    """
usage: sl metadata ip [options]

Get primary ip address
"""
    action = 'ip'

    def _execute(self, _):
        return MetadataManager().get('primary_ip')


class ProvisionState(MetaRunnable):
    """
usage: sl metadata provision_state [options]

Get provision state
"""
    action = 'provision_state'

    def _execute(self, _):
        return MetadataManager().get('provision_state')


class Tags(MetaRunnable):
    """
usage: sl metadata tags [options]

List tags
"""
    action = 'tags'

    def _execute(self, _):
        return listing(MetadataManager().get('tags'), separator=',')


class UserMetadata(CLIRunnable):
    """
usage: sl metadata user_data [options]

Get user-defined data
"""
    action = 'user_data'

    def _execute(self, _):
        """ Returns user metadata """
        userdata = MetadataManager().get('user_data')
        if userdata:
            return userdata
        else:
            raise CLIAbort("No user metadata.")


class Network(MetaRunnable):
    """
usage: sl metadata network (<public> | <private>) [options]

Get details about the public or private network
"""
    action = 'network'

    def _execute(self, args):
        meta = MetadataManager()
        if args['<public>']:
            table = KeyValueTable(['Name', 'Value'])
            table.align['Name'] = 'r'
            table.align['Value'] = 'l'
            network = meta.public_network()
            table.add_row([
                'mac addresses',
                listing(network['mac_addresses'], separator=',')])
            table.add_row([
                'router', network['router']])
            table.add_row([
                'vlans', listing(network['vlans'], separator=',')])
            table.add_row([
                'vlan ids',
                listing(network['vlan_ids'], separator=',')])
            return table

        if args['<private>']:
            table = KeyValueTable(['Name', 'Value'])
            table.align['Name'] = 'r'
            table.align['Value'] = 'l'
            network = meta.private_network()
            table.add_row([
                'mac addresses',
                listing(network['mac_addresses'], separator=',')])
            table.add_row([
                'router', network['router']])
            table.add_row([
                'vlans', listing(network['vlans'], separator=',')])
            table.add_row([
                'vlan ids',
                listing(network['vlan_ids'], separator=',')])
            return table
