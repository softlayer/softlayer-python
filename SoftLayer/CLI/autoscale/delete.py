"""Delete autoscale."""
# :license: MIT, see LICENSE for more details.
import click
import SoftLayer

from SoftLayer.CLI.command import SLCommand as SLCommand
from SoftLayer.CLI import environment
from SoftLayer.managers.autoscale import AutoScaleManager


@click.command(cls=SLCommand)
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """Delete this group and destroy all members of it.

    Example: slcli autoscale delete autoscaleId

    """

    autoscale = AutoScaleManager(env.client)

    try:
        autoscale.delete(identifier)
        click.secho("%s deleted successfully" % identifier, fg='green')
    except SoftLayer.SoftLayerAPIError as ex:
        click.secho("Failed to delete %s\n%s" % (identifier, ex), fg='red')
