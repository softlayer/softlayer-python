"""Set the user VPN password."""
# :license: MIT, see LICENSE for more details.

import click
import SoftLayer

from SoftLayer.CLI.command import SLCommand as SLCommand
from SoftLayer.CLI import environment
from SoftLayer.CLI import helpers


@click.command(cls=SLCommand, )
@click.argument('identifier')
@click.option('--password', required=True, help="Your new VPN password")
@environment.pass_env
def cli(env, identifier, password):
    """Set the user VPN password.

    Example: slcli user vpn-password 123456 --password=Mypassword1.
    """

    mgr = SoftLayer.UserManager(env.client)
    user_id = helpers.resolve_id(mgr.resolve_ids, identifier, 'username')
    result = mgr.update_vpn_password(user_id, password)
    if result:
        click.secho("Successfully updated user VPN password.", fg='green')
