"""List all options for ordering a file storage."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI.command import SLCommand
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting

PACKAGE_STORAGE = 759


@click.command(cls=SLCommand)
@click.argument('location', required=False)
@click.option('--prices', '-p', is_flag=True,
              help='Use --prices to list the server item prices, and to list the Item Prices by location,'
                   'add it to the --prices option using location short name, e.g. --prices dal13')
@environment.pass_env
def cli(env, prices, location=None):
    """List all options for ordering a block storage"""

    order_manager = SoftLayer.OrderingManager(env.client)
    items = order_manager.get_items(PACKAGE_STORAGE)
    datacenters = order_manager.get_regions(PACKAGE_STORAGE, location)

    tables = []
    network = SoftLayer.NetworkManager(env.client)

    pods = network.get_closed_pods()

    if datacenters != []:
        datacenter_table = formatting.Table(['Id', 'Description', 'KeyName'], title='Datacenter')

        for datacenter in datacenters:
            closure = []
            for pod in pods:
                if datacenter['location']['location']['name'] in str(pod['name']):
                    closure.append(pod['name'])

            notes = '-'
            if len(closure) > 0:
                notes = 'closed soon: %s' % (', '.join(closure))
            datacenter_table.add_row([datacenter['location']['locationId'],
                                      datacenter.get('description'),
                                      datacenter['keyname'], notes])
        tables.append(datacenter_table)
    else:
        raise exceptions.CLIAbort('Location does not exit.')

    tables.append(_file_ios_get_table(items, prices))
    tables.append(_file_storage_table(items, prices))
    tables.append(_file_snapshot_get_table(items, prices))
    env.fout(tables)


def _file_ios_get_table(items, prices):
    if prices:
        table = formatting.Table(['Id', 'Description', 'KeyName', 'Prices'], title='IOPS')
        for item in items:
            if item['itemCategory']['categoryCode'] == 'storage_tier_level':
                table.add_row([item.get('id'), item.get('description'),
                               item.get('keyName'), item['prices'][0]['recurringFee']])
    else:
        table = formatting.Table(['Id', 'Description', 'KeyName'], title='IOPS')
        for item in items:
            if item['itemCategory']['categoryCode'] == 'storage_tier_level':
                table.add_row([item.get('id'), item.get('description'),
                               item.get('keyName')])
    table.sortby = 'Id'
    table.align = 'l'
    return table


def _file_storage_table(items, prices):
    if prices:
        table = formatting.Table(['Id', 'Description', 'KeyName', 'Capacity Minimum', 'Prices'], title='Storage')
        for item in items:
            if item['itemCategory']['categoryCode'] == 'performance_storage_space':
                table.add_row([item.get('id'), item.get('description'),
                               item.get('keyName'), item.get('capacityMinimum') or '-',
                               item['prices'][0]['recurringFee']])
    else:
        table = formatting.Table(['Id', 'Description', 'KeyName', 'Capacity Minimum'], title='Storage')
        for item in items:
            if item['itemCategory']['categoryCode'] == 'performance_storage_space':
                table.add_row([item.get('id'), item.get('description'),
                               item.get('keyName'), item.get('capacityMinimum') or '-', ])
    table.sortby = 'Id'
    table.align = 'l'
    return table


def _file_snapshot_get_table(items, prices):
    if prices:
        table = formatting.Table(['Id', 'Description', 'KeyName', 'Prices'], title='Snapshot')
        for item in items:
            if item['itemCategory']['categoryCode'] == 'storage_snapshot_space':
                table.add_row([item.get('id'), item.get('description'),
                               item.get('keyName'), item['prices'][0]['recurringFee']])
    else:
        table = formatting.Table(['Id', 'Description', 'KeyName'], title='Snapshot')
        for item in items:
            if item['itemCategory']['categoryCode'] == 'storage_snapshot_space':
                table.add_row([item.get('id'), item.get('description'),
                               item.get('keyName')])
    table.sortby = 'Id'
    table.align = 'l'
    return table
