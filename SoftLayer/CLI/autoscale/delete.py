"""Delete autoscale."""
# :license: MIT, see LICENSE for more details.

import click

from SoftLayer.CLI import environment
from SoftLayer.managers.autoscale import AutoScaleManager


@click.command()
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """Delete this group and destroy all members of it.

    Example: slcli autoscale delete autoscaleId

    """

    autoscale = AutoScaleManager(env.client)
    result = autoscale.delete(identifier)

    if result:
        click.secho("%s deleted successfully" % identifier, fg='green')
