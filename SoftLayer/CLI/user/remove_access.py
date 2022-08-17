"""User remove access to devices."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.argument('identifier')
@click.option('--hardware', '-h',
              help="Display hardware this user has access to.")
@click.option('--virtual', '-v',
              help="Display virtual guests this user has access to.")
@click.option('--dedicated', '-l',
              help="dedicated host ID ")
@environment.pass_env
def cli(env, identifier, hardware, virtual, dedicated):
    """Remove access from a user to an specific device.

    Example: slcli user remove-access 123456 --hardware 123456789
    """

    mgr = SoftLayer.UserManager(env.client)
    device = ''
    result = False
    if hardware:
        device = hardware
        result = mgr.remove_hardware_access(identifier, hardware)

    if virtual:
        device = virtual
        result = mgr.remove_virtual_access(identifier, virtual)

    if dedicated:
        device = dedicated
        result = mgr.remove_dedicated_access(identifier, dedicated)

    if result:
        click.secho("Remove to access to device: %s" % device, fg='green')
    else:
        raise SoftLayer.exceptions.SoftLayerError('You need argument a hardware, virtual or dedicated identifier.\n'
                                                  'E.g slcli user 123456 --hardware 91803794\n'
                                                  '    slcli user 123456 --dedicated 91803793\n'
                                                  '    slcli user 123456 --virtual 91803792')
