"""List package items."""
# :license: MIT, see LICENSE for more details.
import click

from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer.managers import ordering
from SoftLayer.utils import lookup

COLUMNS = ['category', 'keyName', 'description', 'priceId']
COLUMNS_ITEM_PRICES = ['keyName', 'priceId', 'Hourly', 'Monthly', 'CRMax', 'CRMim', 'CRType']
COLUMNS_ITEM_PRICES_LOCATION = ['keyName', 'priceId', 'Hourly', 'Monthly', 'CRMax', 'CRMim', 'CRType']


@click.command()
@click.argument('package_keyname')
@click.option('--keyword', help="A word (or string) used to filter item names.")
@click.option('--category', help="Category code to filter items by")
@click.option('--prices', '-p', default=False, help='Filter Item Prices, prices(DEFAULT False)')
@click.option('--location', '-l', type=click.STRING, help='To filter the item prices by location, enter the Location '
                                                          'keyName e.g. AMSTERDAM02')
@environment.pass_env
def cli(env, package_keyname, keyword, category, prices, location):
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

    if location and prices:
        raise exceptions.CLIAbort("Please select --prices or --location to get the prices, not both")

    _filter = {'items': {}}
    if keyword:
        _filter['items']['description'] = {'operation': '*= %s' % keyword}
    if category:
        _filter['items']['categories'] = {'categoryCode': {'operation': '_= %s' % category}}

    items = manager.list_items(package_keyname, filter=_filter)
    sorted_items = sort_items(items)

    categories = sorted_items.keys()
    if prices:
        table = formatting.Table(COLUMNS_ITEM_PRICES, title="CRMax = CapacityRestrictionMaximum, "
                                                            "CRMin = CapacityRestrictionMinimum, "
                                                            "CRType = CapacityRestrictionType")
        table = _item_list_prices(categories, sorted_items, table)
    elif location:
        table = formatting.Table(COLUMNS_ITEM_PRICES_LOCATION, title="CRMax = CapacityRestrictionMaximum, "
                                                                     "CRMin = CapacityRestrictionMinimum, "
                                                                     "CRType = CapacityRestrictionType")
        location_prices = manager.get_item_prices_by_location(location, package_keyname)
        table = _location_item_prices(location_prices, table)
    else:
        table = formatting.Table(COLUMNS)
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


def _item_list_prices(categories, sorted_items, table):
    """Add the item prices cost and capacity restriction to the table"""
    for catname in sorted(categories):
        for item in sorted_items[catname]:
            for price in item['prices']:
                if not price.get('locationGroupId'):
                    table.add_row([item['keyName'], price['id'],
                                   get_item_price_data(price, 'hourlyRecurringFee'),
                                   get_item_price_data(price, 'recurringFee'),
                                   get_item_price_data(price, 'capacityRestrictionMaximum'),
                                   get_item_price_data(price, 'capacityRestrictionMinimum'),
                                   get_item_price_data(price, 'capacityRestrictionType')])
    return table


def get_item_price_data(price, item_attribute):
    """Given an SoftLayer_Product_Item_Price, returns its default price data"""
    result = '-'
    if item_attribute in price:
        result = price[item_attribute]
    return result


def _location_item_prices(location_prices, table):
    """Get a specific data from HS price.

    :param price: Hardware Server price.
    :param string item: Hardware Server price data.
    """
    table.sortby = 'keyName'
    table.align = 'l'
    for price in location_prices:
        table.add_row(
            [price['item']['keyName'], price['id'],
             _get_price_data(price, 'hourlyRecurringFee'),
             _get_price_data(price, 'recurringFee'),
             _get_price_data(price, 'capacityRestrictionMaximum'),
             _get_price_data(price, 'capacityRestrictionMinimum'),
             _get_price_data(price, 'capacityRestrictionType')
             ])
    return table


def _get_price_data(price, item):
    """Get a specific data from HS price.

    :param price: Hardware Server price.
    :param string item: Hardware Server price data.
    """
    result = '-'
    if item in price:
        result = price[item]
    return result
