"""List number of file storage volumes per datacenter."""
# :license: MIT, see LICENSE for more details.

import click
import SoftLayer
from SoftLayer.CLI import columns as column_helper
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting

COLUMNS = [
    column_helper.Column('Datacenter',
                         ('serviceResource', 'datacenter', 'name'),
                         mask="serviceResource.datacenter.name"),
    column_helper.Column('Count',
                         '',
                         mask=None)
]

DEFAULT_COLUMNS = [
    'Datacenter',
    'Count'
]


@click.command()
@click.option('--datacenter', '-d', help='Datacenter shortname')
@click.option('--sortby', help='Column to sort by', default='Datacenter')
@click.option('--columns',
              callback=column_helper.get_formatter(COLUMNS),
              help='Columns to display. Options: {0}'.format(
                  ', '.join(column.name for column in COLUMNS)),
              default=','.join(DEFAULT_COLUMNS))
@environment.pass_env
def cli(env, sortby, columns, datacenter):
    """List number of file storage volumes per datacenter."""
    file_manager = SoftLayer.FileStorageManager(env.client)
    mask = "mask[serviceResource[datacenter[name]],"\
           "replicationPartners[serviceResource[datacenter[name]]]]"
    file_volumes = file_manager.list_file_volumes(datacenter=datacenter,
                                                  mask=mask)

    datacenters = dict()
    for volume in file_volumes:
        service_resource = volume['serviceResource']
        if 'datacenter' in service_resource:
            datacenter_name = service_resource['datacenter']['name']
            if datacenter_name not in datacenters.keys():
                datacenters[datacenter_name] = 1
            else:
                datacenters[datacenter_name] += 1

    table = formatting.KeyValueTable(columns.columns)
    table.sortby = sortby
    for datacenter_name in datacenters:
        table.add_row([datacenter_name, datacenters[datacenter_name]])
    env.fout(table)
