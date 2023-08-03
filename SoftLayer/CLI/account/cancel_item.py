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
    """Cancel the resource or service for a billing item.

    By default the billing item will be canceled on the next bill date and
    reclaim of the resource will begin shortly after the cancellation
    """

    manager = AccountManager(env.client)
    item = manager.cancel_item(identifier)

    if item:
        env.fout(f"Item: {identifier} was cancelled.")
