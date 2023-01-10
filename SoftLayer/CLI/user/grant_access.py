"""User grant access to devices."""
# :license: MIT, see LICENSE for more details.

import click
import SoftLayer

from SoftLayer.CLI.command import SLCommand as SLCommand
from SoftLayer.CLI import environment


@click.command(cls=SLCommand, )
@click.argument('identifier')
@click.option('--hardware', help="Hardware ID")
@click.option('--virtual', help="Virtual Guest ID")
@click.option('--dedicated', help="dedicated host ID")
@environment.pass_env
def cli(env, identifier, hardware, virtual, dedicated):
    """Grant access from a user to an specific device.

    Example: slcli user grant-access 123456 --hardware 123456789
    """

    mgr = SoftLayer.UserManager(env.client)
    result = False
    if hardware:
        result = mgr.grant_hardware_access(identifier, hardware)
        if result:
            click.secho("Grant to access to hardware: %s" % hardware, fg='green')

    if virtual:
        result = mgr.grant_virtual_access(identifier, virtual)
        if result:
            click.secho("Grant to access to virtual guest: %s" % virtual, fg='green')

    if dedicated:
        result = mgr.grant_dedicated_access(identifier, dedicated)
        if result:
            click.secho("Grant to access to dedicated host: %s" % dedicated, fg='green')

    if not result:
        raise SoftLayer.exceptions.SoftLayerError('You need argument a hardware, virtual or dedicated identifier.\n'
                                                  'E.g slcli user grant-access 123456 --hardware 91803794\n'
                                                  '    slcli user grant-access 123456 --dedicated 91803793\n'
                                                  '    slcli user grant-access 123456 --virtual 91803792')
