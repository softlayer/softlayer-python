"""Assign block storage subnets to the given host id."""
# :license: MIT, see LICENSE for more details.

import click
import SoftLayer
from SoftLayer.CLI import environment


@click.command()
@click.argument('access_id', type=int)
@click.option('--subnet-id', multiple=True, type=int,
              help="ID of the subnets to assign; e.g.: --subnet-id 1234")
@environment.pass_env
def cli(env, access_id, subnet_id):
    """Assign block storage subnets to the given host id.

    access_id is the host_id obtained by: slcli block access-list <volume_id>

    SoftLayer_Account::iscsiisolationdisabled must be False to use this command
    """
    try:
        subnet_ids = list(subnet_id)
        block_manager = SoftLayer.BlockStorageManager(env.client)
        assigned_subnets = block_manager.assign_subnets_to_acl(access_id, subnet_ids)

        for subnet in assigned_subnets:
            message = "Successfully assigned subnet id: {} to allowed host id: {}".format(subnet, access_id)
            click.echo(message)

        failed_to_assign_subnets = list(set(subnet_ids) - set(assigned_subnets))
        for subnet in failed_to_assign_subnets:
            message = "Failed to assign subnet id: {} to allowed host id: {}".format(subnet, access_id)
            click.echo(message)

    except SoftLayer.SoftLayerAPIError as ex:
        message = "Unable to assign subnets.\nReason: {}".format(ex.faultString)
        click.echo(message)
