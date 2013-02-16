#!/usr/bin/env python
""" Find details about this machine """
from SoftLayer.metadata import MetadataManager
from SoftLayer.CLI import CLIRunnable, Table, listing, CLIAbort


class BackendMacAddresses(CLIRunnable):
    """ backend mac addresses """
    action = 'backend_mac'

    @staticmethod
    def execute(client, args):
        return listing(MetadataManager().get('backend_mac'), separator=',')


class Datacenter(CLIRunnable):
    """ datacenter name """
    action = 'datacenter'

    @staticmethod
    def execute(client, args):
        return MetadataManager().get('datacenter')


class DatacenterId(CLIRunnable):
    """ datacenter id """
    action = 'datacenter_id'

    @staticmethod
    def execute(client, args):
        return MetadataManager().get('datacenter_id')


class FrontendMacAddresses(CLIRunnable):
    """ frontend mac addresses """
    action = 'frontend_mac'

    @staticmethod
    def execute(client, args):
        return listing(MetadataManager().get('frontend_mac'), separator=',')


class FullyQualifiedDomainName(CLIRunnable):
    """ fully qualified domain name """
    action = 'fqdn'

    @staticmethod
    def execute(client, args):
        return MetadataManager().get('fqdn')


class Hostname(CLIRunnable):
    """ hostname """
    action = 'hostname'

    @staticmethod
    def execute(client, args):
        return MetadataManager().get('hostname')


class Id(CLIRunnable):
    """ id """
    action = 'id'

    @staticmethod
    def execute(client, args):
        return MetadataManager().get('id')


class PrimaryBackendIpAddress(CLIRunnable):
    """ primary backend ip address """
    action = 'primary_backend_ip'

    @staticmethod
    def execute(client, args):
        return MetadataManager().get('primary_backend_ip')


class PrimaryIpAddress(CLIRunnable):
    """ primary ip address """
    action = 'primary_ip'

    @staticmethod
    def execute(client, args):
        return MetadataManager().get('primary_ip')


class ProvisionState(CLIRunnable):
    """ provision state """
    action = 'provision_state'

    @staticmethod
    def execute(client, args):
        return MetadataManager().get('provision_state')


class Tags(CLIRunnable):
    """ tags """
    action = 'tags'

    @staticmethod
    def execute(client, args):
        return listing(MetadataManager().get('tags'), separator=',')


class UserMetadata(CLIRunnable):
    """ user-defined data """
    action = 'user_data'

    @staticmethod
    def execute(client, args):
        userdata = MetadataManager().get('user_data')
        if userdata:
            return userdata
        else:
            raise CLIAbort("No user metadata.")


class Network(CLIRunnable):
    """ details about either the public or private network """
    action = 'network'

    @staticmethod
    def add_additional_args(parser):
        parser.add_argument(
            'network_type',
            help="Which type of network to get the details for",
            default='public',
            choices=['public', 'private']
        )

    @staticmethod
    def execute(client, args):
        meta = MetadataManager()
        if args.network_type == 'public':
            t = Table(['Name', 'Value'])
            t.align['Name'] = 'r'
            t.align['Value'] = 'l'
            network = meta.public_network()
            t.add_row([
                'mac addresses',
                listing(network['mac_addresses'], separator=',')])
            t.add_row([
                'router', network['routers']])
            t.add_row([
                'vlans', listing(network['vlans'], separator=',')])
            t.add_row([
                'vlan ids',
                listing(network['vlan_ids'], separator=',')])
            return t

        if args.network_type == 'private':
            t = Table(['Name', 'Value'])
            t.align['Name'] = 'r'
            t.align['Value'] = 'l'
            network = meta.private_network()
            t.add_row([
                'mac addresses',
                listing(network['mac_addresses'], separator=',')])
            t.add_row([
                'router', network['routers']])
            t.add_row([
                'vlans', listing(network['vlans'], separator=',')])
            t.add_row([
                'vlan ids',
                listing(network['vlan_ids'], separator=',')])
            return t
