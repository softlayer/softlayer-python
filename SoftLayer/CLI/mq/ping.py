"""Ping the SoftLayer Message Queue service."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions


@click.command()
@click.option('--datacenter', help="Datacenter, E.G.: dal05")
@click.option('--network',
              type=click.Choice(['public', 'private']),
              help="Network type")
@environment.pass_env
def cli(env, datacenter, network):
    """Ping the SoftLayer Message Queue service."""

    manager = SoftLayer.MessagingManager(env.client)
    okay = manager.ping(datacenter=datacenter, network=network)
    if okay:
        env.fout('OK')
    else:
        exceptions.CLIAbort('Ping failed')
