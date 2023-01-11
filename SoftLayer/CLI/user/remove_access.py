"""User remove access to devices."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.argument('identifier')
@click.option('--hardware', help="Hardware ID")
@click.option('--virtual', help="Virtual Guest ID")
@click.option('--dedicated', help="Dedicated host ID ")
@environment.pass_env
def cli(env, identifier, hardware, virtual, dedicated):
    """Remove access from a user to an specific device.

    Example: slcli user remove-access 123456 --hardware 123456789
    """

    mgr = SoftLayer.UserManager(env.client)
    result = False
    if hardware:
        result = mgr.remove_hardware_access(identifier, hardware)
        if result:
            click.secho("Remove to access to hardware: %s" % hardware, fg='green')

    if virtual:
        result = mgr.remove_virtual_access(identifier, virtual)
        if result:
            click.secho("Remove to access to virtual guest: %s" % virtual, fg='green')

    if dedicated:
        result = mgr.remove_dedicated_access(identifier, dedicated)
        if result:
            click.secho("Remove to access to dedicated host: %s" % dedicated, fg='green')

    if not result:
        raise SoftLayer.exceptions.SoftLayerError('You need argument a hardware, virtual or dedicated identifier.\n'
                                                  'E.g slcli user remove-access 123456 --hardware 91803794\n'
                                                  '    slcli user remove-access 123456 --dedicated 91803793\n'
                                                  '    slcli user remove-access 123456 --virtual 91803792')
