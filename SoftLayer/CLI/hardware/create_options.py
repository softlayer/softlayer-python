"""Server order options for a given chassis."""
# :license: MIT, see LICENSE for more details.

import click

from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.managers import hardware


@click.command()
@click.argument('location', required=False)
@click.option('--prices', '-p', is_flag=True, help='Use --prices to list the server item prices, and '
                                                   'to list the Item Prices by location, add it to the '
                                                   '--prices option using location KeyName, e.g. --prices AMSTERDAM02')
@environment.pass_env
def cli(env, prices, location=None):
    """Server order options for a given chassis."""

    hardware_manager = hardware.HardwareManager(env.client)
    options = hardware_manager.get_create_options()

    tables = []

    # Datacenters
    dc_table = formatting.Table(['Datacenter', 'Value'], title="Datacenters")
    dc_table.sortby = 'Value'
    dc_table.align = 'l'
    for location_info in options['locations']:
        dc_table.add_row([location_info['name'], location_info['key']])
    tables.append(dc_table)

    if prices:
        _preset_prices_table(options['sizes'], tables)
        _os_prices_table(options['operating_systems'], tables)
        _port_speed_prices_table(options['port_speeds'], tables)
        _extras_prices_table(options['extras'], tables)
        if location:
            location_prices = hardware_manager.get_hardware_item_prices(location)
            _location_item_prices(location_prices, tables)
    else:
        # Presets
        preset_table = formatting.Table(['Size', 'Value'], title="Sizes")
        preset_table.sortby = 'Value'
        preset_table.align = 'l'
        for size in options['sizes']:
            preset_table.add_row([size['name'], size['key']])
        tables.append(preset_table)

        # Operating systems
        os_table = formatting.Table(['OS', 'Key', 'Reference Code'], title="Operating Systems")
        os_table.sortby = 'Key'
        os_table.align = 'l'
        for operating_system in options['operating_systems']:
            os_table.add_row([operating_system['name'], operating_system['key'], operating_system['referenceCode']])
        tables.append(os_table)

        # Port speed
        port_speed_table = formatting.Table(['Network', 'Speed', 'Key'], title="Network Options")
        port_speed_table.sortby = 'Speed'
        port_speed_table.align = 'l'
        for speed in options['port_speeds']:
            port_speed_table.add_row([speed['name'], speed['speed'], speed['key']])
        tables.append(port_speed_table)

        # Extras
        extras_table = formatting.Table(['Extra Option', 'Value'], title="Extras")
        extras_table.sortby = 'Value'
        extras_table.align = 'l'
        for extra in options['extras']:
            extras_table.add_row([extra['name'], extra['key']])
        tables.append(extras_table)

    env.fout(formatting.listing(tables, separator='\n'))


def _preset_prices_table(sizes, tables):
    """Shows Server Preset options prices.

    :param [] sizes: List of Hardware Server sizes.
    :param tables: Table formatting.
    """
    preset_prices_table = formatting.Table(['Size', 'Value', 'Hourly', 'Monthly'], title="Sizes Prices")
    preset_prices_table.sortby = 'Value'
    preset_prices_table.align = 'l'
    for size in sizes:
        preset_prices_table.add_row([size['name'], size['key'], "%.4f" % size['hourlyRecurringFee'],
                                     "%.4f" % size['recurringFee']])
    tables.append(preset_prices_table)


def _os_prices_table(operating_systems, tables):
    """Shows Server Operating Systems prices cost and capacity restriction.

    :param [] operating_systems: List of Hardware Server operating systems.
    :param tables: Table formatting.
    """
    os_prices_table = formatting.Table(['OS Key', 'Hourly', 'Monthly', 'Restriction'],
                                       title="Operating Systems Prices")
    os_prices_table.sortby = 'OS Key'
    os_prices_table.align = 'l'
    for operating_system in operating_systems:
        for price in operating_system['prices']:
            cr_max = _get_price_data(price, 'capacityRestrictionMaximum')
            cr_min = _get_price_data(price, 'capacityRestrictionMinimum')
            cr_type = _get_price_data(price, 'capacityRestrictionType')
            os_prices_table.add_row(
                [operating_system['key'],
                 _get_price_data(price, 'hourlyRecurringFee'),
                 _get_price_data(price, 'recurringFee'),
                 "%s - %s %s" % (cr_min, cr_max, cr_type)])
    tables.append(os_prices_table)


def _port_speed_prices_table(port_speeds, tables):
    """Shows Server Port Speeds prices cost and capacity restriction.

    :param [] port_speeds: List of Hardware Server Port Speeds.
    :param tables: Table formatting.
    """
    port_speed_prices_table = formatting.Table(['Key', 'Speed', 'Hourly', 'Monthly', 'Restriction'],
                                               title="Network Options Prices")
    port_speed_prices_table.sortby = 'Speed'
    port_speed_prices_table.align = 'l'
    for speed in port_speeds:
        for price in speed['prices']:
            cr_max = _get_price_data(price, 'capacityRestrictionMaximum')
            cr_min = _get_price_data(price, 'capacityRestrictionMinimum')
            cr_type = _get_price_data(price, 'capacityRestrictionType')
            port_speed_prices_table.add_row(
                [speed['key'], speed['speed'],
                 _get_price_data(price, 'hourlyRecurringFee'),
                 _get_price_data(price, 'recurringFee'),
                 "%s - %s %s" % (cr_min, cr_max, cr_type)])
    tables.append(port_speed_prices_table)


def _extras_prices_table(extras, tables):
    """Shows Server extras prices cost and capacity restriction.

    :param [] extras: List of Hardware Server Extras.
    :param tables: Table formatting.
    """
    extras_prices_table = formatting.Table(['Extra Option Key', 'Hourly', 'Monthly', 'Restriction'],
                                           title="Extras Prices")
    extras_prices_table.align = 'l'
    for extra in extras:
        for price in extra['prices']:
            cr_max = _get_price_data(price, 'capacityRestrictionMaximum')
            cr_min = _get_price_data(price, 'capacityRestrictionMinimum')
            cr_type = _get_price_data(price, 'capacityRestrictionType')
            extras_prices_table.add_row(
                [extra['key'],
                 _get_price_data(price, 'hourlyRecurringFee'),
                 _get_price_data(price, 'recurringFee'),
                 "%s - %s %s" % (cr_min, cr_max, cr_type)])
    tables.append(extras_prices_table)


def _get_price_data(price, item):
    """Get a specific data from HS price.

    :param price: Hardware Server price.
    :param string item: Hardware Server price data.
    """
    result = '-'
    if item in price:
        result = price[item]
    return result


def _location_item_prices(location_prices, tables):
    """Get a specific data from HS price.

    :param price: Hardware Server price.
    :param string item: Hardware Server price data.
    """
    location_prices_table = formatting.Table(['keyName', 'priceId', 'Hourly', 'Monthly', 'Restriction'])
    location_prices_table.sortby = 'keyName'
    location_prices_table.align = 'l'
    for price in location_prices:
        cr_max = _get_price_data(price, 'capacityRestrictionMaximum')
        cr_min = _get_price_data(price, 'capacityRestrictionMinimum')
        cr_type = _get_price_data(price, 'capacityRestrictionType')
        location_prices_table.add_row(
            [price['item']['keyName'], price['id'],
             _get_price_data(price, 'hourlyRecurringFee'),
             _get_price_data(price, 'recurringFee'),
             "%s - %s %s" % (cr_min, cr_max, cr_type)])
    tables.append(location_prices_table)
