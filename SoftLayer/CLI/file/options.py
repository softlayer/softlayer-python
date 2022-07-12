"""List all options for ordering a file storage."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI.command import SLCommand
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting


PACKAGE_STORAGE = 759


@click.command(cls=SLCommand)
@environment.pass_env
def cli(env):
    """List all options for ordering a file storage"""

    order_manager = SoftLayer.OrderingManager(env.client)
    items = order_manager.get_items(PACKAGE_STORAGE)
    datacenters = order_manager.get_regions(PACKAGE_STORAGE)

    iops_table = formatting.Table(['Id', 'Description', 'KeyName'], title='IOPS')
    snapshot_table = formatting.Table(['Id', 'Description', 'KeyName'], title='Snapshot')
    storage_table = formatting.Table(['Id', 'Description', 'KeyName'], title='Storage')
    datacenter_table = formatting.Table(['Id', 'Description', 'KeyName'], title='Datacenter')

    for datacenter in datacenters:
        datacenter_table.add_row([datacenter['location']['locationId'],
                                  datacenter.get('description'),
                                  datacenter['keyname']])

    for item in items:
        if item['itemCategory']['categoryCode'] == 'performance_storage_space':
            storage_table.add_row([item.get('id'), item.get('description'),
                                   item.get('keyName')])

        if item['itemCategory']['categoryCode'] == 'storage_tier_level':
            iops_table.add_row([item.get('id'), item.get('description'),
                                item.get('keyName')])

        if item['itemCategory']['categoryCode'] == 'storage_snapshot_space':
            snapshot_table.add_row([item.get('id'), item.get('description'),
                                    item.get('keyName')])

    env.fout(datacenter_table)
    env.fout(iops_table)
    env.fout(storage_table)
    env.fout(snapshot_table)
