"""Remove a user VS notification entry."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """Remove a user VS notification entry."""

    virtual = SoftLayer.VSManager(env.client)

    result = virtual.remove_notification(identifier)

    if result:
        env.fout("The virtual server notification instance: {} was deleted.".format(identifier))
