"""Get the all Os available."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@environment.pass_env
def cli(env):
    """Get the all Os available"""

    table = formatting.KeyValueTable(['Id', 'KeyName', 'Description', 'Price', 'Setup Fee'])
    table.align['name'] = 'r'
    table.align['value'] = 'l'
    manager = SoftLayer.OrderingManager(env.client)
    _filter = {"items": {"prices": {"categories": {"categoryCode": {"operation": "os"}}}}}
    operations = manager.get_items(storage_filter=_filter, package_id=46)

    for operation_system in operations:
        table.add_row([operation_system.get('id'), operation_system.get('keyName'), operation_system.get('description'),
                       operation_system['prices'][0]['laborFee'],
                       operation_system['prices'][0]['setupFee']])

    env.fout(table)
