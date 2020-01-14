"""List block storage assigned subnets for the given host id."""
# :license: MIT, see LICENSE for more details.

import click
import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting


COLUMNS = [
    'id',
    'createDate',
    'networkIdentifier',
    'cidr'
]


@click.command()
@click.argument('access_id')
@environment.pass_env
def cli(env, access_id):
    """List block storage assigned subnets for the given host id.

    access_id is the allowed_host_id from slcli block access-list
    """

    block_manager = SoftLayer.BlockStorageManager(env.client)
    subnets = block_manager.get_subnets_in_acl(access_id)

    table = formatting.Table(COLUMNS)
    for subnet in subnets:
        row = ["{0}".format(subnet['id']),
               "{0}".format(subnet['createDate']),
               "{0}".format(subnet['networkIdentifier']),
               "{0}".format(subnet['cidr'])]
        table.add_row(row)

    env.fout(table)
