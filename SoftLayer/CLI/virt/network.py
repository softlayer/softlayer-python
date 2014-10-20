"""Manage network settings."""
# :license: MIT, see LICENSE for more details.

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import helpers

import click


@click.command()
@click.argument('identifier')
@click.argument('network-type', type=click.Choice(['public', 'private']))
@click.option('--speed',
              required=True,
              help="Port speed. 0 disables the port.",
              type=click.Choice(['0', '10', '100', '1000', '10000']))
@environment.pass_env
def cli(env, identifier, network_type, speed):
    """Manage network settings."""

    public = (network_type == 'public')

    vsi = SoftLayer.VSManager(env.client)
    vs_id = helpers.resolve_id(vsi.resolve_ids, identifier, 'VS')

    vsi.change_port_speed(vs_id, public, speed)
