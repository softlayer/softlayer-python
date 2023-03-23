"""Delete a provisioning script"""
# :license: MIT, see LICENSE for more details.

import click
import SoftLayer

from SoftLayer.CLI.command import SLCommand as SLCommand
from SoftLayer.CLI import environment
from SoftLayer.managers.account import AccountManager as AccountManager


@click.command(cls=SLCommand)
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """Delete a provisioning script"""

    manager = AccountManager(env.client)

    try:
        manager.delete_provisioning(identifier)
        click.secho("%s deleted successfully" % identifier, fg='green')
    except SoftLayer.SoftLayerAPIError as ex:
        click.secho("Failed to delete %s\n%s" % (identifier, ex), fg='red')
