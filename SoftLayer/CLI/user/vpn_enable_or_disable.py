"""Enable or Disable vpn for a user."""
# :license: MIT, see LICENSE for more details.


import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import helpers


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.argument('user')
@environment.pass_env
def vpn_enable(env, user):
    """Enable vpn for a user.

    Example::
        slcli user vpn-enable 1234567
    """

    mgr = SoftLayer.UserManager(env.client)
    user_id = helpers.resolve_id(mgr.resolve_ids, user, 'username')

    result = mgr.vpn_enable_or_disable(user_id, True)
    message = f"{user} vpn is successfully enabled"

    if result:
        click.secho(message, fg='green')


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.argument('user')
@environment.pass_env
def vpn_disable(env, user):
    """Disable vpn for a user.

    Example::
        slcli user vpn-disable 1234567
    """

    mgr = SoftLayer.UserManager(env.client)
    user_id = helpers.resolve_id(mgr.resolve_ids, user, 'username')

    result = mgr.vpn_enable_or_disable(user_id, False)
    message = f"{user} vpn is successfully disabled"

    if result:
        click.secho(message, fg='green')
