"""Remove SSL certificate."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """Remove SSL certificate."""

    manager = SoftLayer.SSLManager(env.client)
    if not (env.skip_confirmations or formatting.no_going_back('yes')):
        raise exceptions.CLIAbort("Aborted.")

    manager.remove_certificate(identifier)
