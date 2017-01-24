"""Edit details of a security group."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions


@click.command()
@click.argument('group_id')
@click.option('--name', '-n',
              help="The name of the security group")
@click.option('--description', '-d',
              help="The description of the security group")
@environment.pass_env
def cli(env, group_id, name, description):
    """Edit details of a security group."""
    mgr = SoftLayer.NetworkManager(env.client)
    data = {}
    if name:
        data['name'] = name
    if description:
        data['description'] = description

    if not mgr.edit_securitygroup(group_id, **data):
        raise exceptions.CLIAbort("Failed to edit security group")
