"""Assigns the global IP to a target."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import helpers


# pylint: disable=unused-argument
def targetipcallback(ctx, param, value):
    """This is here to allow for using --target-id in some cases. Takes the first value and returns it"""
    if value:
        return value[0]
    return value


@click.command(cls=SoftLayer.CLI.command.SLCommand, epilog="More information about types and identifiers "
               "on https://sldn.softlayer.com/reference/services/SoftLayer_Network_Subnet/route/")
@click.argument('globalip')
@click.argument('targetip', nargs=-1, callback=targetipcallback)
@click.option('--target', type=click.Choice(['vlan', 'ip', 'hardware', 'vsi']),
              help='choose the type. vlan, ip, hardware, vsi')
@click.option('--target-id', help='The identifier for the destination resource to route this subnet to.')
@environment.pass_env
def cli(env, globalip, targetip, target, target_id):
    """Assigns the GLOBALIP to TARGETIP.

    GLOBALIP should be either the Global IP address, or the SoftLayer_Network_Subnet_IpAddress_Global id
    See `slcli globalip list`
    TARGETIP should be either the target IP address, or the SoftLayer_Network_Subnet_IpAddress id
    See `slcli subnet list`
    Example::

        slcli globalip assign 12345678 9.111.123.456
        This command assigns Global IP address with ID 12345678 to a target device whose IP address is 9.111.123.456

        slcli globalip assign 123.4.5.6 6.5.4.123
        Global IPs can be specified by their IP address
    """
    mgr = SoftLayer.NetworkManager(env.client)
    # Find SoftLayer_Network_Subnet_IpAddress_Global::id
    global_ip_id = helpers.resolve_id(mgr.resolve_global_ip_ids, globalip,  name='Global IP')

    # Find Global IPs SoftLayer_Network_Subnet::id
    mask = "mask[id,ipAddress[subnetId]]"
    subnet = env.client.call('SoftLayer_Network_Subnet_IpAddress_Global', 'getObject', id=global_ip_id, mask=mask)
    subnet_id = subnet.get('ipAddress', {}).get('subnetId')

    # For backwards compatibility
    if target_id:
        targetip = target_id

    mgr.route(subnet_id, 'SoftLayer_Network_Subnet_IpAddress', targetip)
