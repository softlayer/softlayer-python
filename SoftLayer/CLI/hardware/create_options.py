"""Server order options for a given chassis."""
# :license: MIT, see LICENSE for more details.

import click

from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.managers import account
from SoftLayer.managers import hardware


@click.command()
@click.argument('location', required=False)
@click.option('--prices', '-p', is_flag=True,
              help='Use --prices to list the server item prices, and to list the Item Prices by location,'
                   'add it to the --prices option using location short name, e.g. --prices dal13')
@environment.pass_env
def cli(env, prices, location=None):
    """Server order options for a given chassis."""

    hardware_manager = hardware.HardwareManager(env.client)
    account_manager = account.AccountManager(env.client)
    options = hardware_manager.get_create_options(location)
    routers = account_manager.get_routers(location=location)
    tables = []

    # Datacenters
    dc_table = formatting.Table(['Datacenter', 'Value'], title="Datacenters")
    dc_table.sortby = 'Value'
    dc_table.align = 'l'
    for location_info in options['locations']:
        dc_table.add_row([location_info['name'], location_info['key']])
    tables.append(dc_table)

    tables.append(_preset_prices_table(options['sizes'], prices))
    tables.append(_os_prices_table(options['operating_systems'], prices))
    tables.append(_port_speed_prices_table(options['port_speeds'], prices))
    tables.append(_extras_prices_table(options['extras'], prices))
    tables.append(_get_routers(routers))

    # since this is multiple tables, this is required for a valid JSON object to be rendered.
    env.fout(formatting.listing(tables, separator='\n'))


def _preset_prices_table(sizes, prices=False):
    """Shows Server Preset options prices.

    :param [] sizes: List of Hardware Server sizes.
    :param prices: Create a price table or not
    """
    if prices:
        table = formatting.Table(['Size', 'Value', 'Hourly', 'Monthly'], title="Sizes")
        for size in sizes:
            if size.get('hourlyRecurringFee', 0) + size.get('recurringFee', 0) + 1 > 0:
                table.add_row([size['name'], size['key'], "%.4f" % size['hourlyRecurringFee'],
                               "%.4f" % size['recurringFee']])
    else:
        table = formatting.Table(['Size', 'Value'], title="Sizes")
        for size in sizes:
            table.add_row([size['name'], size['key']])
    table.sortby = 'Value'
    table.align = 'l'
    return table


def _os_prices_table(operating_systems, prices=False):
    """Shows Server Operating Systems prices cost and capacity restriction.

    :param [] operating_systems: List of Hardware Server operating systems.
    :param prices: Create a price table or not
    """
    if prices:
        table = formatting.Table(['Key', 'Hourly', 'Monthly', 'Restriction'],
                                 title="Operating Systems")
        for operating_system in operating_systems:
            for price in operating_system['prices']:
                cr_max = _get_price_data(price, 'capacityRestrictionMaximum')
                cr_min = _get_price_data(price, 'capacityRestrictionMinimum')
                cr_type = _get_price_data(price, 'capacityRestrictionType')
                table.add_row(
                    [operating_system['key'],
                     _get_price_data(price, 'hourlyRecurringFee'),
                     _get_price_data(price, 'recurringFee'),
                     "%s - %s %s" % (cr_min, cr_max, cr_type)])
    else:
        table = formatting.Table(['OS', 'Key', 'Reference Code'], title="Operating Systems")
        for operating_system in operating_systems:
            table.add_row([operating_system['name'], operating_system['key'], operating_system['referenceCode']])

    table.sortby = 'Key'
    table.align = 'l'
    return table


def _port_speed_prices_table(port_speeds, prices=False):
    """Shows Server Port Speeds prices cost and capacity restriction.

    :param [] port_speeds: List of Hardware Server Port Speeds.
    :param prices: Create a price table or not
    """
    if prices:
        table = formatting.Table(['Key', 'Speed', 'Hourly', 'Monthly'], title="Network Options")
        for speed in port_speeds:
            for price in speed['prices']:
                table.add_row(
                    [speed['key'], speed['speed'],
                     _get_price_data(price, 'hourlyRecurringFee'),
                     _get_price_data(price, 'recurringFee')])
    else:
        table = formatting.Table(['Network', 'Speed', 'Key'], title="Network Options")
        for speed in port_speeds:
            table.add_row([speed['name'], speed['speed'], speed['key']])
    table.sortby = 'Speed'
    table.align = 'l'
    return table


def _extras_prices_table(extras, prices=False):
    """Shows Server extras prices cost and capacity restriction.

    :param [] extras: List of Hardware Server Extras.
    :param prices: Create a price table or not
    """
    if prices:
        table = formatting.Table(['Key', 'Hourly', 'Monthly'], title="Extras")

        for extra in extras:
            for price in extra['prices']:
                table.add_row(
                    [extra['key'],
                     _get_price_data(price, 'hourlyRecurringFee'),
                     _get_price_data(price, 'recurringFee')])
    else:
        table = formatting.Table(['Extra Option', 'Key'], title="Extras")
        for extra in extras:
            table.add_row([extra['name'], extra['key']])
    table.sortby = 'Key'
    table.align = 'l'
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


def _get_routers(routers):
    """Get all routers information

    :param routers: Routers data
    """

    table = formatting.Table(["id", "hostname", "name"], title='Routers')
    for router in routers:
        table.add_row([router['id'],
                       router['hostname'],
                       router['topLevelLocation']['longName'], ])
    table.align = 'l'
    return table
