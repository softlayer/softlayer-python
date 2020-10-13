"""Cancels a billing item."""
# :license: MIT, see LICENSE for more details.
import click

from SoftLayer.CLI import environment
from SoftLayer.managers.account import AccountManager as AccountManager


@click.command()
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """Cancels a billing item."""

    manager = AccountManager(env.client)
    item = manager.cancel_item(identifier)

    env.fout(item)
