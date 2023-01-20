"""Grants a user access to a given device"""
# :license: MIT, see LICENSE for more details.

import click
import SoftLayer

from SoftLayer.CLI.command import SLCommand as SLCommand
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions


@click.command(cls=SLCommand, )
@click.argument('identifier')
@click.option('--hardware', help="Hardware ID")
@click.option('--virtual', help="Virtual Guest ID")
@click.option('--dedicated', help="dedicated host ID")
@environment.pass_env
def cli(env, identifier, hardware, virtual, dedicated):
    """Grants a user access to a given device.

    Example: slcli user grant-access 123456 --hardware 123456789
    """

    mgr = SoftLayer.UserManager(env.client)
    result = False
    if hardware:
        result = mgr.grant_hardware_access(identifier, hardware)
        if result:
            click.secho(f"User {identifier} has been given access to hardware {hardware}", fg='green')

    if virtual:
        result = mgr.grant_virtual_access(identifier, virtual)
        if result:
            click.secho(f"User {identifier} has been given access to hardware {virtual}", fg='green')

    if dedicated:
        result = mgr.grant_dedicated_access(identifier, dedicated)
        if result:
            click.secho(f"User {identifier} has been given access to hardware {dedicated}", fg='green')

    if not result:
        raise exceptions.CLIAbort('A device option is required.\n'
                                  'E.g slcli user grant-access 123456 --hardware 91803794\n'
                                  '    slcli user grant-access 123456 --dedicated 91803793\n'
                                  '    slcli user grant-access 123456 --virtual 91803792')
