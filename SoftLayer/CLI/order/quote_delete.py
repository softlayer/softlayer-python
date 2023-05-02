"""Delete the quote of an order"""
# :license: MIT, see LICENSE for more details.
import click

from SoftLayer.CLI.command import SLCommand as SLCommand
from SoftLayer.CLI import environment
from SoftLayer.managers import ordering


@click.command(cls=SLCommand)
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """Delete the quote of an order"""

    manager = ordering.OrderingManager(env.client)
    result = manager.delete_quote(identifier)

    if result:
        env.fout(f"Quote id: {identifier} was deleted.")
