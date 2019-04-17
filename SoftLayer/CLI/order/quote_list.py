"""List active quotes on an account."""
# :license: MIT, see LICENSE for more details.
import click

from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.managers import ordering
from SoftLayer.utils import clean_time


@click.command()
@environment.pass_env
def cli(env):
    """List all active quotes on an account"""
    table = formatting.Table([
        'Id', 'Name', 'Created', 'Expiration', 'Status', 'Package Name', 'Package Id'
    ])
    table.align['Name'] = 'l'
    table.align['Package Name'] = 'r'
    table.align['Package Id'] = 'l'

    manager = ordering.OrderingManager(env.client)
    items = manager.get_quotes()

    for item in items:
        package = item['order']['items'][0]['package']
        table.add_row([
            item.get('id'),
            item.get('name'),
            clean_time(item.get('createDate')),
            clean_time(item.get('modifyDate')),
            item.get('status'),
            package.get('keyName'),
            package.get('id')
        ])
    env.fout(table)
