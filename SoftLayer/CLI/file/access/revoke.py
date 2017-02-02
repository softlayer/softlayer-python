"""Revokes hosts' access on a specific file volume."""
# :license: MIT, see LICENSE for more details.

import click
import SoftLayer
from SoftLayer.CLI import environment


@click.command()
@click.argument('volume_id')
@click.option('--hardware-id', '-h', multiple=True,
              help='The id of one SoftLayer_Hardware'
              ' to revoke authorization')
@click.option('--virtual-id', '-v', multiple=True,
              help='The id of one SoftLayer_Virtual_Guest'
              ' to revoke authorization')
@click.option('--ip-address-id', '-i', multiple=True,
              help='The id of one SoftLayer_Network_Subnet_IpAddress'
              ' to revoke authorization')
@click.option('--ip-address', multiple=True,
              help='An IP address to revoke authorization')
@click.option('--subnet-id', '-s', multiple=True,
              help='The id of one SoftLayer_Network_Subnet'
              ' to revoke authorization')
@environment.pass_env
def cli(env, volume_id, hardware_id, virtual_id, ip_address_id,
        ip_address, subnet_id):
    """Revokes authorization for hosts accessing a given volume"""
    file_manager = SoftLayer.FileStorageManager(env.client)
    ip_address_id_list = list(ip_address_id)

    # Convert actual IP Addresses to their SoftLayer ids
    if ip_address is not None:
        network_manager = SoftLayer.NetworkManager(env.client)
        for ip_address_value in ip_address:
            ip_address_object = network_manager.ip_lookup(ip_address_value)
            ip_address_id_list.append(ip_address_object['id'])

    file_manager.deauthorize_host_to_volume(volume_id,
                                            hardware_id,
                                            virtual_id,
                                            ip_address_id_list,
                                            subnet_id)

    # If no exception was raised, the command succeeded
    click.echo('Access to %s was revoked for the specified hosts' % volume_id)
