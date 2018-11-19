"""Toggle the IPMI interface on and off."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import helpers


@click.command()
@click.argument('identifier')
@click.option('--enabled',
              type=click.BOOL,
              help="Whether to enable or disable the interface.")
@environment.pass_env
def cli(env, identifier, enabled):
    """Toggle the IPMI interface on and off"""

    mgr = SoftLayer.HardwareManager(env.client)
    hw_id = helpers.resolve_id(mgr.resolve_ids, identifier, 'hardware')
    result = env.client['Hardware_Server'].toggleManagementInterface(enabled, id=hw_id)
    env.fout(result)
