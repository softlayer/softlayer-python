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
    """List package items used for ordering.

    The items listed can be used with `slcli order place` to specify
    the items that are being ordered in the package.

    Package keynames can be retrieved using `slcli order package-list`

    \b
    Example:
        # List all items in the VSI package
        slcli order item-list CLOUD_SERVER

    The --keyword option is used to filter items by name.
    The --category option is used to filter items by category.
    Both --keyword and --category can be used together.

    \b
    Example:
        # List Ubuntu OSes from the os category of the Bare Metal package
        slcli order item-list BARE_METAL_SERVER --category os --keyword ubuntu

    """
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
