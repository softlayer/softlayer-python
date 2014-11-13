"""Remove SSL certificate."""
# :license: MIT, see LICENSE for more details.

import softlayer
from softlayer.cli import environment
from softlayer.cli import exceptions
from softlayer.cli import formatting

import click


@click.command()
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """Remove SSL certificate."""

    manager = softlayer.SSLManager(env.client)
    if env.skip_confirmations or formatting.no_going_back('yes'):
        manager.remove_certificate(identifier)
    raise exceptions.CLIAbort("Aborted.")
