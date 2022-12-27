"""allows you to change the route of your Account Owned subnets."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment

target_types = {'vlan': 'SoftLayer_Network_Vlan',
                'ip': 'SoftLayer_Network_Subnet_IpAddress',
                'hardware': 'SoftLayer_Hardware_Server',
                'vsi': 'SoftLayer_Virtual_Guest'}


@click.command(cls=SoftLayer.CLI.command.SLCommand, epilog="More information about types and identifiers "
               "on https://sldn.softlayer.com/reference/services/SoftLayer_Network_Subnet/route/")
@click.argument('identifier')
@click.option('--target', type=click.Choice(['vlan', 'ip', 'hardware', 'vsi']),
              help='choose the type. vlan, ip, hardware, vsi')
@click.option('--target-resource', help='An appropriate identifier for the specified $type. '
                                        'Some types have multiple identifier. ')
@environment.pass_env
def cli(env, identifier, target, target_resource):
    """Assigns the subnet to a target."""

    mgr = SoftLayer.NetworkManager(env.client)
    mgr.route(identifier, target_types.get(target), target_resource)
