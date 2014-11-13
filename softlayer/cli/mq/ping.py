"""Ping the SoftLayer Message Queue service."""
# :license: MIT, see LICENSE for more details.

import softlayer
from softlayer.cli import environment
from softlayer.cli import exceptions

import click


@click.command()
@click.option('--datacenter', help="Datacenter, E.G.: dal05")
@click.option('--network',
              type=click.Choice(['public', 'private']),
              help="Network type")
@environment.pass_env
def cli(env, datacenter, network):
    """Ping the SoftLayer Message Queue service."""

    manager = softlayer.MessagingManager(env.client)
    okay = manager.ping(datacenter=datacenter, network=network)
    if okay:
        return 'OK'
    else:
        exceptions.CLIAbort('Ping failed')
