"""List package presets."""
# :license: MIT, see LICENSE for more details.

import click

from SoftLayer.CLI.command import SLCommand as SLCommand
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.managers import ordering

COLUMNS = ['name',
           'keyName',
           'description', ]


@click.command(cls=SLCommand)
@click.argument('package_keyname')
@click.option('--keyword',
              help="A word (or string) used to filter preset names.")
@click.option('--prices', '-p', is_flag=True, help='Use --prices to list the server item prices, e.g. --prices')
@environment.pass_env
def cli(env, package_keyname, keyword, prices):
    """List package presets.

    .. Note::
        Presets are set CPU / RAM / Disk allotments. You still need to specify required items.
        Some packages do not have presets.

    ::

        # List the presets for Bare Metal servers
        slcli order preset-list BARE_METAL_SERVER

        # List the Bare Metal server presets that include a GPU
        slcli order preset-list BARE_METAL_SERVER --keyword gpu

    """

    tables = []
    table = formatting.Table(COLUMNS)
    manager = ordering.OrderingManager(env.client)

    _filter = {}
    if keyword:
        _filter = {'activePresets': {'name': {'operation': '*= %s' % keyword}}}
    presets = manager.list_presets(package_keyname, filter=_filter)

    if prices:
        table_prices = formatting.Table(['keyName', 'priceId', 'Hourly', 'Monthly', 'Restriction', 'Location'])
        for price in presets:
            locations = []
            if price['locations'] != []:
                for location in price['locations']:
                    locations.append(location['name'])
            cr_max = get_item_price_data(price['prices'][0], 'capacityRestrictionMaximum')
            cr_min = get_item_price_data(price['prices'][0], 'capacityRestrictionMinimum')
            cr_type = get_item_price_data(price['prices'][0], 'capacityRestrictionType')
            table_prices.add_row([price['keyName'], price['id'],
                                  get_item_price_data(price['prices'][0], 'hourlyRecurringFee'),
                                  get_item_price_data(price['prices'][0], 'recurringFee'),
                                  "%s - %s %s" % (cr_min, cr_max, cr_type), str(locations)])
        tables.append(table_prices)

    else:
        for preset in presets:
            table.add_row([
                str(preset['name']).strip(),
                str(preset['keyName']).strip(),
                str(preset['description']).strip()
            ])
        tables.append(table)
    env.fout(tables)


def get_item_price_data(price, item_attribute):
    """Given an SoftLayer_Product_Item_Price, returns its default price data"""
    result = '-'
    if item_attribute in price:
        result = price[item_attribute]
    return result
