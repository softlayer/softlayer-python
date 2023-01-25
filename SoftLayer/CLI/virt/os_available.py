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

    table = formatting.KeyValueTable(['id', 'keyName', 'Description', 'price', 'setup fee'])
    table.align['name'] = 'r'
    table.align['value'] = 'l'
    vsi = SoftLayer.VSManager(env.client)
    operations = vsi.get_os()
    for operation_system in operations:
        table.add_row([operation_system.get('id'), operation_system.get('keyName'), operation_system.get('description'),
                       operation_system['prices'][0]['laborFee'],
                       operation_system['prices'][0]['setupFee']])

    env.fout(table)
