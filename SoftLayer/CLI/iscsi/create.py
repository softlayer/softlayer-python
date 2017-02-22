"""Creates an iSCSI target."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment


@click.command()
@click.option('--size',
              type=click.Choice(['20', '40', '80', '100', '250', '500', '1000', '2000', '4000', \
              '8000', '12000']),
              required=True,
              help="Size of the iSCSI volume to create (in Gigabytes)")
@click.option('--datacenter',
              required=True,
              help="Datacenter shortname (sng01, dal05, ...)")
@environment.pass_env
def cli(env, size, datacenter):
    """Creates an iSCSI target."""

    iscsi_mgr = SoftLayer.ISCSIManager(env.client)
    iscsi_mgr.create_iscsi(size=int(size), location=datacenter)
