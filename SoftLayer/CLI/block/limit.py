"""List number of block storage volumes limit per datacenter."""
# :license: MIT, see LICENSE for more details.

import click
import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting

DEFAULT_COLUMNS = [
    'Datacenter',
    'MaximumAvailableCount',
    'ProvisionedCount'
]


@click.command()
@click.option('--sortby', help='Column to sort by', default='Datacenter')
@environment.pass_env
def cli(env, sortby):
    """List number of block storage volumes limit per datacenter."""
    block_manager = SoftLayer.BlockStorageManager(env.client)
    block_volumes = block_manager.list_block_volume_limit()

    table = formatting.KeyValueTable(DEFAULT_COLUMNS)
    table.sortby = sortby
    for volume in block_volumes:
        datacenter_name = volume['datacenterName']
        maximum_available_count = volume['maximumAvailableCount']
        provisioned_count = volume['provisionedCount']
        table.add_row([datacenter_name, maximum_available_count, provisioned_count])
    env.fout(table)
