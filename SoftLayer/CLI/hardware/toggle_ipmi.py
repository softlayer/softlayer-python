"""Toggle the IPMI interface on and off."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import helpers


@click.command()
@click.argument('identifier')
@click.option('--enable/--disable', default=True,
              help="Whether enable (DEFAULT) or disable the interface.")
@environment.pass_env
def cli(env, identifier, enable):
    """Toggle the IPMI interface on and off"""

    mgr = SoftLayer.HardwareManager(env.client)
    hw_id = helpers.resolve_id(mgr.resolve_ids, identifier, 'hardware')
    result = env.client['Hardware_Server'].toggleManagementInterface(enable, id=hw_id)
    env.fout(result)
