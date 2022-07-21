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

    network = SoftLayer.NetworkManager(env.client)

    pods = network.get_closed_pods()

    iops_table = formatting.Table(['Id', 'Description', 'KeyName'], title='IOPS')
    snapshot_table = formatting.Table(['Id', 'Description', 'KeyName'], title='Snapshot')
    file_storage_table = formatting.Table(['Id', 'Description', 'KeyName'], title='Storage')
    datacenter_table = formatting.Table(['Id', 'Description', 'KeyName'], title='Datacenter')

    file_storage_table.align['Description'] = 'l'
    file_storage_table.align['KeyName'] = 'l'
    file_storage_table.sortby = 'Id'

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

    for item_file in items:
        if item_file['itemCategory']['categoryCode'] == 'performance_storage_space':
            file_storage_table.add_row([item_file.get('id'), item_file.get('description'),
                                        item_file.get('keyName')])

        if item_file['itemCategory']['categoryCode'] == 'storage_tier_level':
            iops_table.add_row([item_file.get('id'), item_file.get('description'),
                                item_file.get('keyName')])

        if item_file['itemCategory']['categoryCode'] == 'storage_snapshot_space':
            snapshot_table.add_row([item_file.get('id'), item_file.get('description'),
                                    item_file.get('keyName')])

    env.fout(datacenter_table)
    env.fout(iops_table)
    env.fout(file_storage_table)
    env.fout(snapshot_table)
