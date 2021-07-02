"""List number of block storage volumes per datacenter."""
# :license: MIT, see LICENSE for more details.

import click
import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting

DEFAULT_COLUMNS = [
    'Datacenter',
    'Count'
]


@click.command()
@click.option('--datacenter', '-d', help='Datacenter shortname')
@click.option('--sortby', help='Column to sort by', default='Datacenter')
@environment.pass_env
def cli(env, sortby, datacenter):
    """List number of block storage volumes per datacenter."""
    block_manager = SoftLayer.BlockStorageManager(env.client)
    mask = "mask[serviceResource[datacenter[name]],"\
           "replicationPartners[serviceResource[datacenter[name]]]]"
    block_volumes = block_manager.list_block_volumes(datacenter=datacenter,
                                                     mask=mask)

    # cycle through all block volumes and count datacenter occurences.
    datacenters = dict()
    for volume in block_volumes:
        service_resource = volume['serviceResource']
        if 'datacenter' in service_resource:
            datacenter_name = service_resource['datacenter']['name']
            if datacenter_name not in datacenters.keys():
                datacenters[datacenter_name] = 1
            else:
                datacenters[datacenter_name] += 1

    table = formatting.KeyValueTable(DEFAULT_COLUMNS)
    table.sortby = sortby
    for key, value in datacenters.items():
        table.add_row([key, value])
    env.fout(table)
