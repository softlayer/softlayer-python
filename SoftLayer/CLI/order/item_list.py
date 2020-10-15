"""List package items."""
# :license: MIT, see LICENSE for more details.
import click

from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.managers import ordering
from SoftLayer.utils import lookup

COLUMNS = ['category', 'keyName', 'description', 'priceId']
COLUMNS_ITEM_PRICES = ['keyName', 'priceId', 'Hourly', 'Monthly', 'Restriction']
COLUMNS_ITEM_PRICES_LOCATION = ['keyName', 'priceId', 'Hourly', 'Monthly', 'Restriction']


@click.command()
@click.argument('package_keyname')
@click.option('--keyword', '-k', help="A word (or string) used to filter item names.")
@click.option('--category', '-c', help="Category code to filter items by")
@click.option('--prices', '-p', is_flag=True, help='Use --prices to list the server item prices, and to list the '
                                                   'Item Prices by location, add it to the --prices option using '
                                                   'location KeyName, e.g. --prices AMSTERDAM02')
@click.argument('location', required=False)
@environment.pass_env
def cli(env, package_keyname, keyword, category, prices, location=None):
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
    manager = ordering.OrderingManager(env.client)

    tables = []

    _filter = {'items': {}}
    if keyword:
        _filter['items']['description'] = {'operation': '*= %s' % keyword}
    if category:
        _filter['items']['categories'] = {'categoryCode': {'operation': '_= %s' % category}}

    items = manager.list_items(package_keyname, filter=_filter)
    sorted_items = sort_items(items)

    categories = sorted_items.keys()
    if prices:
        _item_list_prices(categories, sorted_items, tables)
        if location:
            location_prices = manager.get_item_prices_by_location(location, package_keyname)
            _location_item_prices(location_prices, location, tables)
    else:
        table_items_detail = formatting.Table(COLUMNS)
        for category_name in sorted(categories):
            for item in sorted_items[category_name]:
                table_items_detail.add_row([category_name, item['keyName'], item['description'], get_price(item)])
        tables.append(table_items_detail)
    env.fout(formatting.listing(tables, separator='\n'))


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


def _item_list_prices(categories, sorted_items, tables):
    """Add the item prices cost and capacity restriction to the table"""
    table_prices = formatting.Table(COLUMNS_ITEM_PRICES)
    for category in sorted(categories):
        for item in sorted_items[category]:
            for price in item['prices']:
                if not price.get('locationGroupId'):
                    cr_max = get_item_price_data(price, 'capacityRestrictionMaximum')
                    cr_min = get_item_price_data(price, 'capacityRestrictionMinimum')
                    cr_type = get_item_price_data(price, 'capacityRestrictionType')
                    table_prices.add_row([item['keyName'], price['id'],
                                          get_item_price_data(price, 'hourlyRecurringFee'),
                                          get_item_price_data(price, 'recurringFee'),
                                          "%s - %s %s" % (cr_min, cr_max, cr_type)])
    tables.append(table_prices)


def get_item_price_data(price, item_attribute):
    """Given an SoftLayer_Product_Item_Price, returns its default price data"""
    result = '-'
    if item_attribute in price:
        result = price[item_attribute]
    return result


def _location_item_prices(location_prices, location, tables):
    """Add a location prices table to tables.

    :param list location_prices : Location prices.
    :param string location : Location.
    :param list tables: Table list to add location prices table.
    """
    location_prices_table = formatting.Table(COLUMNS_ITEM_PRICES_LOCATION, title="Item Prices for %s" % location)
    location_prices_table.sortby = 'keyName'
    location_prices_table.align = 'l'
    for price in location_prices:
        cr_max = get_item_price_data(price, 'capacityRestrictionMaximum')
        cr_min = get_item_price_data(price, 'capacityRestrictionMinimum')
        cr_type = get_item_price_data(price, 'capacityRestrictionType')
        location_prices_table.add_row(
            [price['item']['keyName'], price['id'],
             get_item_price_data(price, 'hourlyRecurringFee'),
             get_item_price_data(price, 'recurringFee'),
             "%s - %s %s" % (cr_min, cr_max, cr_type)])
    tables.append(location_prices_table)
