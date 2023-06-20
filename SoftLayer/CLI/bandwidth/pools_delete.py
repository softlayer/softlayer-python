"""Delete bandwidth pool."""
# :license: MIT, see LICENSE for more details.
import click

from SoftLayer import BandwidthManager
from SoftLayer.CLI.command import SLCommand as SLCommand
from SoftLayer.CLI import environment


@click.command(cls=SLCommand)
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """Delete bandwidth pool."""

    manager = BandwidthManager(env.client)
    bandwidth_pool = manager.delete_pool(identifier)

    if bandwidth_pool:
        env.fout(f"Bandwidth pool with ID {identifier} was programmed to will delete")
