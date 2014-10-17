"""Upgrade a virtual server"""
# :license: MIT, see LICENSE for more details.

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers

import click


class MemoryType(click.ParamType):
    """Memory type"""
    name = 'integer'

    def convert(self, value, param, ctx):
        try:
            return int(value) / 1024
        except ValueError:
            self.fail('%s is not an integer that is divisable by 1024'
                      % value, param, ctx)

MEM_TYPE = MemoryType()


@click.command(epilog="""Note: SoftLayer automatically reboots the VS once
upgrade request is placed. The VS is halted until the Upgrade transaction is
completed. However for Network, no reboot is required.""")
@click.argument('identifier')
@click.option('--cpu', type=click.INT, help="Number of CPU cores")
@click.option('--private',
              is_flag=True,
              help="CPU core will be on a dedicated host server.")
@click.option('--memory', type=MEM_TYPE, help="Memory in megabytes")
@click.option('--network', type=click.INT, help="Network port speed in Mbps")
@environment.pass_env
def cli(env, identifier, cpu, private, memory, network):
    """Upgrade a virtual server"""

    vsi = SoftLayer.VSManager(env.client)

    vs_id = helpers.resolve_id(vsi.resolve_ids, identifier, 'VS')
    if env.skip_confirmations or formatting.confirm(
            "This action will incur charges on your account. "
            "Continue?"):
        if not vsi.upgrade(vs_id,
                           cpus=cpu,
                           memory=memory,
                           nic_speed=network,
                           public=not private):
            raise exceptions.CLIAbort('VS Upgrade Failed')
