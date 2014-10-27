"""Manage NIC settings."""
# :license: MIT, see LICENSE for more details.

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import helpers

import click


@click.command()
@click.argument('identifier')
@click.argument('network', type=click.Choice(['public', 'private']))
@click.option('--speed',
              type=click.Choice(['0', '10', '100', '1000', '10000']),
              help="Port speed. 0 disables the port")
@environment.pass_env
def cli(env, identifier, network, speed):
    """Manage NIC settings."""

    mgr = SoftLayer.HardwareManager(env.client)
    hw_id = helpers.resolve_id(mgr.resolve_ids, identifier, 'hardware')

    mgr.change_port_speed(hw_id, network == 'public', int(speed))
