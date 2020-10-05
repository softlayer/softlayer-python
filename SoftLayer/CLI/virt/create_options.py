"""Virtual server order options."""
# :license: MIT, see LICENSE for more details.
# pylint: disable=too-many-statements
import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting


@click.command(short_help="Get options to use for creating virtual servers.")
@click.argument('location', required=False)
@click.option('--vsi-type', required=False, show_default=True, default='PUBLIC_CLOUD_SERVER',
              type=click.Choice(['PUBLIC_CLOUD_SERVER', 'TRANSIENT_CLOUD_SERVER', 'SUSPEND_CLOUD_SERVER',
                                 'CLOUD_SERVER']),
              help="VS keyName type.")
@click.option('--prices', '-p', is_flag=True,
              help='Use --prices to list the server item prices, and to list the Item Prices by location,'
                   'add it to the --prices option using location short name, e.g. --prices dal13')
@environment.pass_env
def cli(env, vsi_type, prices, location=None):
    """Virtual server order options."""

    vsi = SoftLayer.VSManager(env.client)
    options = vsi.get_create_options(vsi_type, location)

    tables = []

    # Datacenters
    dc_table = formatting.Table(['datacenter', 'Value'], title="Datacenters")
    dc_table.sortby = 'Value'
    dc_table.align = 'l'
    for location_info in options['locations']:
        dc_table.add_row([location_info['name'], location_info['key']])
    tables.append(dc_table)

    if vsi_type == 'CLOUD_SERVER':
        tables.append(guest_core_prices_table(options['guest_core'], prices))
        tables.append(ram_prices_table(options['ram'], prices))
    else:
        tables.append(preset_prices_table(options['sizes'], prices))
    tables.append(os_prices_table(options['operating_systems'], prices))
    tables.append(port_speed_prices_table(options['port_speed'], prices))
    tables.append(database_prices_table(options['database'], prices))
    tables.append(guest_disk_prices_table(options['guest_disk'], prices))
    tables.append(extras_prices_table(options['extras'], prices))

    env.fout(tables)


def preset_prices_table(sizes, prices=False):
    """Shows Server Preset options prices.

    :param [] sizes: List of Hardware Server sizes.
    :param prices: Include pricing information or not.
    """
    preset_price_table = formatting.Table(['Size', 'Value', 'Hourly', 'Monthly'], title="Sizes Prices")
    preset_price_table.sortby = 'Value'
    preset_price_table.align = 'l'

    preset_table = formatting.Table(['Size', 'Value'], title="Sizes")
    preset_table.sortby = 'Value'
    preset_table.align = 'l'

    for size in sizes:
        if (size['hourlyRecurringFee'] > 0) or (size['recurringFee'] > 0):
            preset_price_table.add_row([size['name'], size['key'], "%.4f" % size['hourlyRecurringFee'],
                                        "%.4f" % size['recurringFee']])
        preset_table.add_row([size['name'], size['key']])
    if prices:
        return preset_price_table
    return preset_table


def os_prices_table(operating_systems, prices=False):
    """Shows Server Operating Systems prices cost and capacity restriction.

    :param [] operating_systems: List of Hardware Server operating systems.
    :param prices: Include pricing information or not.
    """
    os_price_table = formatting.Table(['OS Key', 'Hourly', 'Monthly', 'Restriction'],
                                      title="Operating Systems Prices")
    os_price_table.sortby = 'OS Key'
    os_price_table.align = 'l'

    os_table = formatting.Table(['OS', 'Key', 'Reference Code'], title="Operating Systems")
    os_table.sortby = 'Key'
    os_table.align = 'l'

    for operating_system in operating_systems:
        for price in operating_system['prices']:
            cr_max = _get_price_data(price, 'capacityRestrictionMaximum')
            cr_min = _get_price_data(price, 'capacityRestrictionMinimum')
            cr_type = _get_price_data(price, 'capacityRestrictionType')
            os_price_table.add_row(
                [operating_system['key'],
                 _get_price_data(price, 'hourlyRecurringFee'),
                 _get_price_data(price, 'recurringFee'),
                 "%s - %s %s" % (cr_min, cr_max, cr_type)])
        os_table.add_row([operating_system['name'], operating_system['key'], operating_system['referenceCode']])
    if prices:
        return os_price_table
    return os_table


def port_speed_prices_table(port_speeds, prices=False):
    """Shows Server Port Speeds prices cost and capacity restriction.

    :param [] port_speeds: List of Hardware Server Port Speeds.
    :param prices: Include pricing information or not.
    """
    port_speed_price_table = formatting.Table(['Key', 'Speed', 'Hourly', 'Monthly'], title="Network Options Prices")
    port_speed_price_table.sortby = 'Speed'
    port_speed_price_table.align = 'l'

    port_speed_table = formatting.Table(['network', 'Key'], title="Network Options")
    port_speed_table.sortby = 'Key'
    port_speed_table.align = 'l'

    for speed in port_speeds:
        for price in speed['prices']:
            port_speed_price_table.add_row(
                [speed['key'], speed['speed'],
                 _get_price_data(price, 'hourlyRecurringFee'),
                 _get_price_data(price, 'recurringFee')])
        port_speed_table.add_row([speed['name'], speed['key']])
    if prices:
        return port_speed_price_table
    return port_speed_table


def extras_prices_table(extras, prices=False):
    """Shows Server extras prices cost and capacity restriction.

    :param [] extras: List of Hardware Server Extras.
    :param prices: Include pricing information or not.
    """
    extras_price_table = formatting.Table(['Extra Option Key', 'Hourly', 'Monthly'], title="Extras Prices")
    extras_price_table.align = 'l'

    extras_table = formatting.Table(['Extra Option', 'Value'], title="Extras")
    extras_table.sortby = 'Value'
    extras_table.align = 'l'

    for extra in extras:
        for price in extra['prices']:
            extras_price_table.add_row(
                [extra['key'],
                 _get_price_data(price, 'hourlyRecurringFee'),
                 _get_price_data(price, 'recurringFee')])
        extras_table.add_row([extra['name'], extra['key']])
    if prices:
        return extras_price_table
    return extras_table


def ram_prices_table(ram_list, prices=False):
    """Shows Server Port Speeds prices cost and capacity restriction.

    :param [] ram_list: List of Virtual Server Ram.
    :param prices: Include pricing information or not.
    """
    ram_price_table = formatting.Table(['Key', 'Hourly', 'Monthly'], title="Ram Prices")
    ram_price_table.sortby = 'Key'
    ram_price_table.align = 'l'

    ram_table = formatting.Table(['memory', 'Value'], title="RAM")
    ram_table.sortby = 'Value'
    ram_table.align = 'l'

    for ram in ram_list:
        for price in ram['prices']:
            ram_price_table.add_row(
                [ram['key'],
                 _get_price_data(price, 'hourlyRecurringFee'),
                 _get_price_data(price, 'recurringFee')])
        ram_table.add_row([ram['name'], ram['key']])
    if prices:
        return ram_price_table
    return ram_table


def database_prices_table(database_list, prices=False):
    """Shows Server Port Speeds prices cost and capacity restriction.

    :param [] database_list: List of Virtual Server database.
    :param prices: Include pricing information or not.
    """
    database_price_table = formatting.Table(['Key', 'Hourly', 'Monthly', 'Restriction'], title="Data Base Prices")
    database_price_table.sortby = 'Key'
    database_price_table.align = 'l'

    database_table = formatting.Table(['database', 'Value'], title="Databases")
    database_table.sortby = 'Value'
    database_table.align = 'l'

    for database in database_list:
        for price in database['prices']:
            cr_max = _get_price_data(price, 'capacityRestrictionMaximum')
            cr_min = _get_price_data(price, 'capacityRestrictionMinimum')
            cr_type = _get_price_data(price, 'capacityRestrictionType')
            database_price_table.add_row(
                [database['key'],
                 _get_price_data(price, 'hourlyRecurringFee'),
                 _get_price_data(price, 'recurringFee'),
                 "%s - %s %s" % (cr_min, cr_max, cr_type)])
        database_table.add_row([database['name'], database['key']])
    if prices:
        return database_price_table
    return database_table


def guest_core_prices_table(guest_core_list, prices=False):
    """Shows Server Port Speeds prices cost and capacity restriction.

    :param [] guest_core_list: List of Virtual Server guest_core.
    :param prices: Include pricing information or not.
    """
    guest_core_price_table = formatting.Table(['Key', 'Hourly', 'Monthly'], title="Guest Core Prices")
    guest_core_price_table.sortby = 'Key'
    guest_core_price_table.align = 'l'

    guest_core_table = formatting.Table(['cpu', 'Value', 'Capacity'], title="Guest_core")
    guest_core_table.sortby = 'Value'
    guest_core_table.align = 'l'

    for guest_core in guest_core_list:
        for price in guest_core['prices']:
            guest_core_price_table.add_row(
                [guest_core['key'],
                 _get_price_data(price, 'hourlyRecurringFee'),
                 _get_price_data(price, 'recurringFee')])
        guest_core_table.add_row([guest_core['name'], guest_core['key'], guest_core['capacity']])
    if prices:
        return guest_core_price_table
    return guest_core_table


def guest_disk_prices_table(guest_disk_list, prices=False):
    """Shows Server Port Speeds prices cost and capacity restriction.

    :param [] guest_disk_list: List of Virtual Server guest_disk.
    :param prices: Include pricing information or not.
    """
    guest_disk_price_table = formatting.Table(['Key', 'Hourly', 'Monthly'], title="Guest Disk Prices")
    guest_disk_price_table.sortby = 'Key'
    guest_disk_price_table.align = 'l'

    guest_disk_table = formatting.Table(['guest_disk', 'Value', 'Capacity', 'Disk'], title="Guest_disks")
    guest_disk_table.sortby = 'Value'
    guest_disk_table.align = 'l'

    for guest_disk in guest_disk_list:
        for price in guest_disk['prices']:
            guest_disk_price_table.add_row(
                [guest_disk['key'],
                 _get_price_data(price, 'hourlyRecurringFee'),
                 _get_price_data(price, 'recurringFee')])
        guest_disk_table.add_row(
            [guest_disk['name'], guest_disk['key'], guest_disk['capacity'], guest_disk['disk']])
    if prices:
        return guest_disk_price_table
    return guest_disk_table


def _get_price_data(price, item):
    """Get a specific data from HS price.

    :param price: Hardware Server price.
    :param string item: Hardware Server price data.
    """
    result = '-'
    if item in price:
        result = price[item]
    return result
