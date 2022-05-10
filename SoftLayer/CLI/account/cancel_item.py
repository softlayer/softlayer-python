"""Cancels a billing item."""
# :license: MIT, see LICENSE for more details.
import click

from SoftLayer.CLI.command import SLCommand as SLCommand
from SoftLayer.CLI import environment
from SoftLayer.managers.account import AccountManager as AccountManager


@click.command(cls=SLCommand)
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """Cancels a billing item."""

    manager = AccountManager(env.client)
    item = manager.cancel_item(identifier)

    if item:
        env.fout("Item: {} was cancelled.".format(identifier))
