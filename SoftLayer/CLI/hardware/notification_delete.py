"""Remove a user hardware notification entry."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """Remove a user hardware notification entry."""

    hardware = SoftLayer.HardwareManager(env.client)

    result = hardware.remove_notification(identifier)

    if result:
        env.fout("The hardware notification instance: {} was deleted.".format(identifier))
