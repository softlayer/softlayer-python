"""allows you to change the route of your Account Owned subnets."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions

target_types = {'vlan': 'SoftLayer_Network_Vlan',
                'ip': 'SoftLayer_Network_Subnet_IpAddress',
                'hardware': 'SoftLayer_Hardware_Server',
                'vsi': 'SoftLayer_Virtual_Guest'}


@click.command(cls=SoftLayer.CLI.command.SLCommand, epilog="More information about types and identifiers "
               "on https://sldn.softlayer.com/reference/services/SoftLayer_Network_Subnet/route/")
@click.argument('identifier')
@click.option('--target', type=click.Choice(['vlan', 'ip', 'hardware', 'vsi']),
              help='choose the type. vlan, ip, hardware, vsi')
@click.option('--target-resource', help='Allows you to change the route of your secondary subnets.'
                                        'Subnets may be routed as either Static or Portable, and that designation is '
                                        'dictated by the routing destination specified.'
                                        'Static subnets have an ultimate routing destination of a single IP address '
                                        'but may not be routed to an existing subnet’s IP address whose '
                                        'subnet is routed as a Static.'
                                        'Portable subnets have an ultimate routing destination of a VLAN.'
                                        'A subnet can be routed to any resource within the same "routing region"'
                                        ' as the subnet itself, usually limited to a single data center.'
                                        'See Also: '
                                        'https://sldn.softlayer.com/reference/services/SoftLayer_Network_Subnet/route/')
@environment.pass_env
def cli(env, identifier, target, target_resource):
    """Assigns the subnet to a target."""

    mgr = SoftLayer.NetworkManager(env.client)
    route = mgr.route(identifier, target_types.get(target), target_resource)

    if route:
        click.secho("Route updated successfully.")
    else:
        raise exceptions.CLIAbort('Failed to route the subnet.')
