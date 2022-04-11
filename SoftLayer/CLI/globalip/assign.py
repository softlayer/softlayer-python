"""Assigns the global IP to a target."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment


@click.command(epilog="More information about types and ")
@click.argument('identifier')
@click.option('--target',
              help='See SLDN docs. '
                   'E.g SoftLayer_Network_Subnet_IpAddress, SoftLayer_Hardware_Server,SoftLayer_Virtual_Guest')
@click.option('--router', help='An appropriate identifier for the specified $type. Some types have multiple identifier')
@environment.pass_env
def cli(env, identifier, target, router):
    """Assigns the global IP to a target."""

    mgr = SoftLayer.NetworkManager(env.client)
    mgr.route(identifier, target, router)
