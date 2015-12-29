"""Authorizes hosts on a specific file volume."""
# :license: MIT, see LICENSE for more details.

import click
import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions


@click.command()
@click.argument('volume_id')
@click.option('--hardware-id', '-h', multiple=True,
              help='The id of one SoftLayer_Hardware to authorize')
@click.option('--virtual-id', '-v', multiple=True,
              help='The id of one SoftLayer_Virtual_Guest to authorize')
@click.option('--ip-address-id', '-i', multiple=True,
              help='The id of one SoftLayer_Network_Subnet_IpAddress'
              ' to authorize')
@click.option('--ip-address', multiple=True,
              help='An IP address to authorize')
@click.option('--subnet-id', '-s', multiple=True,
              help='The id of one SoftLayer_Network_Subnet to authorize')
@environment.pass_env
def cli(env, volume_id, hardware_id, virtual_id, ip_address_id,
        ip_address, subnet_id):
    """Authorizes hosts to access a given volume"""
    file_manager = SoftLayer.FileStorageManager(env.client)
    ip_address_id_list = list(ip_address_id)

    # Convert actual IP Addresses to their SoftLayer ids
    if ip_address is not None:
        network_manager = SoftLayer.NetworkManager(env.client)
        for ip_address_value in ip_address:
            ip_address_object = network_manager.ip_lookup(ip_address_value)
            if ip_address_object == "":
                click.echo("IP Address not found on your account.  " +
                           "Please confirm IP and try again.")
                raise exceptions.ArgumentError('Incorrect IP Address')
            else:
                ip_address_id_list.append(ip_address_object['id'])

    file_manager.authorize_host_to_volume(volume_id,
                                          hardware_id,
                                          virtual_id,
                                          ip_address_id_list,
                                          subnet_id)

    # If no exception was raised, the command succeeded
    click.echo('The specified hosts were authorized to access %s' % volume_id)
