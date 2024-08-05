"""Cancel global IP."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.argument('identifier')
@click.option('-f', '--force', default=False, is_flag=True, help="Force operation without confirmation")
@environment.pass_env
def cli(env, identifier, force):
    """Cancel global IP.

    Example::

        slcli globalip cancel 12345
    """

    mgr = SoftLayer.NetworkManager(env.client)
    global_ip_id = helpers.resolve_id(mgr.resolve_global_ip_ids, identifier, name='global ip')

    if not force:
        if not (env.skip_confirmations or
                formatting.confirm(f"This will cancel the IP address: {global_ip_id} and cannot be undone. Continue?")):
            raise exceptions.CLIAbort('Aborted')

    mgr.cancel_global_ip(global_ip_id)
