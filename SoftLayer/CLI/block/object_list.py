"""List cloud object storage volumes."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@environment.pass_env
def cli(env):
    """List cloud block storage."""
    block_manager = SoftLayer.BlockStorageManager(env.client)

    storages = block_manager.get_cloud_list()

    table = formatting.Table(['Id',
                              'Account name',
                              'Description',
                              'Create Date',
                              'Type'])
    for storage in storages:
        table.add_row([storage.get('id'),
                       storage.get('username'),
                       storage['storageType']['description'],
                       storage['billingItem']['createDate'],
                       storage['storageType']['keyName']])

    env.fout(table)
