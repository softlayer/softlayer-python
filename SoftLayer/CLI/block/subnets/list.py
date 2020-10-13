"""List block storage assigned subnets for the given host id."""
# :license: MIT, see LICENSE for more details.

import click
import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers


COLUMNS = [
    'id',
    'createDate',
    'networkIdentifier',
    'cidr'
]


@click.command()
@click.argument('access_id', type=int)
@environment.pass_env
def cli(env, access_id):
    """List block storage assigned subnets for the given host id.

    access_id is the host_id obtained by: slcli block access-list <volume_id>
    """

    try:
        block_manager = SoftLayer.BlockStorageManager(env.client)
        resolved_id = helpers.resolve_id(block_manager.resolve_ids, access_id, 'Volume Id')
        subnets = block_manager.get_subnets_in_acl(resolved_id)

        table = formatting.Table(COLUMNS)
        for subnet in subnets:
            row = ["{0}".format(subnet['id']),
                   "{0}".format(subnet['createDate']),
                   "{0}".format(subnet['networkIdentifier']),
                   "{0}".format(subnet['cidr'])]
            table.add_row(row)

        env.fout(table)

    except SoftLayer.SoftLayerAPIError as ex:
        message = "Unable to list assigned subnets for access-id: {}.\nReason: {}".format(access_id, ex.faultString)
        click.echo(message)
