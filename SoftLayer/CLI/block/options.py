"""List all options for ordering a block storage."""
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
    items = order_manager.get_items(PACKAGE_STORAGE, mask="mask[categories]")
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

    tables.append(_block_ios_get_table(items, prices))
    tables.append(_block_storage_table(items, prices))
    tables.append(_block_snapshot_get_table(items, prices))
    env.fout(tables)


def _block_ios_get_table(items, prices):
    if prices:
        table = formatting.Table(['Id', 'Description', 'KeyName', 'Prices'], title='IOPS')
        for block_item in items:
            if block_item['itemCategory']['categoryCode'] == 'storage_tier_level':
                table.add_row([block_item.get('id'), block_item.get('description'),
                               block_item.get('keyName'), block_item['prices'][0]['recurringFee']])
    else:
        table = formatting.Table(['Id', 'Description', 'KeyName'], title='IOPS')
        for block_item in items:
            if block_item['itemCategory']['categoryCode'] == 'storage_tier_level':
                table.add_row([block_item.get('id'), block_item.get('description'),
                               block_item.get('keyName')])
    table.sortby = 'KeyName'
    table.align = 'l'
    return table


def _block_storage_table(items, prices):
    if prices:
        table = formatting.Table(['Id', 'Description', 'KeyName', 'Capacity Minimum', 'Prices'], title='Storage')
        for block_item in items:
            if block_item['itemCategory']['categoryCode'] == 'performance_storage_space':
                table.add_row([block_item.get('id'), block_item.get('description'),
                               block_item.get('keyName'), block_item.get('capacityMinimum') or '-',
                               block_item['prices'][0]['recurringFee']])
    else:
        table = formatting.Table(['Id', 'Description', 'KeyName', 'Capacity Minimum'], title='Storage')
        for block_item in items:
            if block_item['itemCategory']['categoryCode'] == 'performance_storage_space':
                table.add_row([block_item.get('id'), block_item.get('description'),
                               block_item.get('keyName'), block_item.get('capacityMinimum') or '-', ])
    table.sortby = 'KeyName'
    table.align = 'l'
    return table


def _block_snapshot_get_table(items, prices):
    if prices:
        table = formatting.Table(['Id', 'Description', 'KeyName', 'Prices'], title='Snapshot')
        for block_item in items:
            if block_item['itemCategory']['categoryCode'] == 'storage_snapshot_space':
                table.add_row([block_item.get('id'), block_item.get('description'),
                               block_item.get('keyName'), block_item['prices'][0]['recurringFee']])
    else:
        table = formatting.Table(['Id', 'Description', 'KeyName'], title='Snapshot')
        for block_item in items:
            if is_snapshot_category(block_item.get('categories', [])):
                table.add_row([block_item.get('id'), block_item.get('description'), block_item.get('keyName')])
    table.sortby = 'KeyName'
    table.align = 'l'
    return table


def is_snapshot_category(categories):
    """Checks if storage_snapshot_space is one of the categories"""
    for item in categories:
        if item.get('categoryCode') == "storage_snapshot_space":
            return True
    return False
