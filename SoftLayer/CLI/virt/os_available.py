"""Get all available Operating Systems."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer

from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@environment.pass_env
def cli(env):
    """Get all available Operating Systems."""

    table = formatting.KeyValueTable(['Id', 'KeyName', 'Description', 'Hourly', 'Monthly', 'Setup'])
    table.align['name'] = 'r'
    table.align['value'] = 'l'
    manager = SoftLayer.OrderingManager(env.client)
    _filter = {"items": {"prices": {"categories": {"categoryCode": {"operation": "os"}}}}}
    # PUBLIC_CLOUD_SERVER = 835
    operations = manager.get_items(storage_filter=_filter, package_id=835)

    for operation_system in operations:
        table.add_row([operation_system.get('id'), operation_system.get('keyName'), operation_system.get('description'),
                       operation_system['prices'][0].get('hourlyRecurringFee') or formatting.blank(),
                       operation_system['prices'][0]['laborFee'],
                       operation_system['prices'][0]['setupFee']])
    env.fout(table)
