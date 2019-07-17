"""List package items."""
# :license: MIT, see LICENSE for more details.
import click

from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.managers import ordering
from SoftLayer.utils import lookup

COLUMNS = ['category', 'keyName', 'description', 'priceId']


@click.command()
@click.argument('package_keyname')
@click.option('--keyword', help="A word (or string) used to filter item names.")
@click.option('--category', help="Category code to filter items by")
@environment.pass_env
def cli(env, package_keyname, keyword, category):
    """List package items used for ordering.

    The item keyNames listed can be used with `slcli order place` to specify
    the items that are being ordered in the package.

    .. Note::
        Items with a numbered category, like disk0 or gpu0, can be included
        multiple times in an order to match how many of the item you want to order.

    ::

        # List all items in the VSI package
        slcli order item-list CLOUD_SERVER

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
    sorted_items = sort_items(items)

    categories = sorted_items.keys()
    for catname in sorted(categories):
        for item in sorted_items[catname]:
            table.add_row([catname, item['keyName'], item['description'], get_price(item)])
    env.fout(table)


def sort_items(items):
    """sorts the items into a dictionary of categories, with a list of items"""

    sorted_items = {}
    for item in items:
        category = lookup(item, 'itemCategory', 'categoryCode')
        if sorted_items.get(category) is None:
            sorted_items[category] = []
        sorted_items[category].append(item)

    return sorted_items


def get_price(item):
    """Given an SoftLayer_Product_Item, returns its default price id"""

    for price in item.get('prices', []):
        if not price.get('locationGroupId'):
            return price.get('id')
    return 0
