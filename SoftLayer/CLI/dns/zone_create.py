"""Create a zone."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.argument('zone')
@environment.pass_env
def cli(env, zone):
    """Create a zone.

    Example::
        slcli dns zone-create ibm.com
        This command creates a zone that is named ibm.com.
"""

    manager = SoftLayer.DNSManager(env.client)
    manager.create_zone(zone)
