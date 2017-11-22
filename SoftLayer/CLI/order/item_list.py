"""List package items."""
# :license: MIT, see LICENSE for more details.

import click

from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.managers import ordering

COLUMNS = ['keyName',
           'description', ]


@click.command()
@click.argument('package_keyname')
@click.option('--keyword',
              help="A word (or string) used to filter item names.")
@click.option('--category',
              help="Category code to filter items by")
@environment.pass_env
def cli(env, package_keyname, keyword, category):
    """List package items."""
    table = formatting.Table(COLUMNS)
    manager = ordering.OrderingManager(env.client)

    _filter = {'items': {}}
    if keyword:
        _filter['items']['description'] = {'operation': '*= %s' % keyword}
    if category:
        _filter['items']['categories'] = {'categoryCode': {'operation': '_= %s' % category}}

    items = manager.list_items(package_keyname, filter=_filter)

    for item in items:
        table.add_row([
            item['keyName'],
            item['description'],
        ])
    env.fout(table)
