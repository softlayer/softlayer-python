"""Delete autoscale."""
# :license: MIT, see LICENSE for more details.

import click

from SoftLayer.CLI import environment
from SoftLayer.managers.autoscale import AutoScaleManager


@click.command()
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """Sets a user's status to CANCEL_PENDING, which will immediately disable the account,

    and will eventually be fully removed from the account by an automated internal process.

    Example: slcli user delete userId

    """

    autoscale = AutoScaleManager(env.client)
    result = autoscale.delete(identifier)

    if result:
        click.secho("%s deleted successfully" % identifier, fg='green')
    else:
        click.secho("Failed to delete %s" % identifier, fg='red')
