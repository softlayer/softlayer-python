"""Removes a user access to a given device."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.argument('identifier')
@click.option('--hardware', help="Hardware ID")
@click.option('--virtual', help="Virtual Guest ID")
@click.option('--dedicated', help="Dedicated host ID ")
@environment.pass_env
def cli(env, identifier, hardware, virtual, dedicated):
    """Removes a user access to a given device.

    Example: slcli user remove-access 123456 --hardware 123456789
    """

    mgr = SoftLayer.UserManager(env.client)
    result = False
    if hardware:
        result = mgr.remove_hardware_access(identifier, hardware)
        if result:
            click.secho(f"Removed access to hardware: {hardware}.", fg='green')

    if virtual:
        result = mgr.remove_virtual_access(identifier, virtual)
        if result:
            click.secho(f"Removed access to virtual guest: {virtual}", fg='green')

    if dedicated:
        result = mgr.remove_dedicated_access(identifier, dedicated)
        if result:
            click.secho(f"Removed access to dedicated host: {dedicated}", fg='green')

    if not result:
        raise exceptions.CLIAbort('A device option is required.\n'
                                  'E.g slcli user remove-access 123456 --hardware 91803794\n'
                                  '    slcli user remove-access 123456 --dedicated 91803793\n'
                                  '    slcli user remove-access 123456 --virtual 91803792')
