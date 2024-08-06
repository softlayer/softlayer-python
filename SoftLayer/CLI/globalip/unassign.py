"""Unassigns a global IP from a target."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import helpers


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """Unroutes IDENTIFIER

    IDENTIFIER should be either the Global IP address, or the SoftLayer_Network_Subnet_IpAddress_Global id
    Example::

        slcli globalip unassign 123456

        slcli globalip unassign 123.43.22.11
"""

    mgr = SoftLayer.NetworkManager(env.client)
    global_ip_id = helpers.resolve_id(mgr.resolve_global_ip_ids, identifier, name='global ip')

    # Find Global IPs SoftLayer_Network_Subnet::id
    mask = "mask[id,ipAddress[subnetId]]"
    subnet = env.client.call('SoftLayer_Network_Subnet_IpAddress_Global', 'getObject', id=global_ip_id, mask=mask)
    subnet_id = subnet.get('ipAddress', {}).get('subnetId')
    mgr.clear_route(subnet_id)
