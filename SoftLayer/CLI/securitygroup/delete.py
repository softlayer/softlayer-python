"""Delete a security group."""
# :license: MIT, see LICENSE for more details.

import click
import SoftLayer
from SoftLayer.CLI import environment


@click.command()
@click.argument('securitygroup_id')
@environment.pass_env
def cli(env, securitygroup_id):
    """Deletes the given security group"""
    mgr = SoftLayer.NetworkManager(env.client)
    mgr.delete_securitygroup(securitygroup_id)
