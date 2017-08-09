"""Delete a security group."""
# :license: MIT, see LICENSE for more details.

import click
import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions


@click.command()
@click.argument('securitygroup_id')
@environment.pass_env
def cli(env, securitygroup_id):
    """Deletes the given security group"""
    mgr = SoftLayer.NetworkManager(env.client)
    if not mgr.delete_securitygroup(securitygroup_id):
        raise exceptions.CLIAbort("Failed to delete security group")
