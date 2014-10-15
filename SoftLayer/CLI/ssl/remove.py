"""Remove SSL certificate"""
# :license: MIT, see LICENSE for more details.

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting

import click


@click.command()
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """Remove SSL certificate"""

    manager = SoftLayer.SSLManager(env.client)
    if env.skip_confirmations or formatting.no_going_back('yes'):
        manager.remove_certificate(identifier)
    raise exceptions.CLIAbort("Aborted.")
