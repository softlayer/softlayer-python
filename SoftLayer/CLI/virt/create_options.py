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
              help="Display options for a specific virtual server packages, for default is PUBLIC_CLOUD_SERVER, "
                   "choose between TRANSIENT_CLOUD_SERVER, SUSPEND_CLOUD_SERVER, CLOUD_SERVER")
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

    if prices:
        preset_prices_table(options['sizes'], tables)
        os_prices_table(options['operating_systems'], tables)
        port_speed_prices_table(options['port_speed'], tables)
        ram_prices_table(options['ram'], tables)
        database_prices_table(options['database'], tables)
        guest_core_prices_table(options['guest_core'], tables)
        guest_disk_prices_table(options['guest_disk'], tables)
        extras_prices_table(options['extras'], tables)
    else:
        # Operation system
        os_table = formatting.Table(['OS', 'Key', 'Reference Code'], title="Operating Systems")
        os_table.sortby = 'Key'
        os_table.align = 'l'

        for operating_system in options['operating_systems']:
            os_table.add_row([operating_system['name'], operating_system['key'], operating_system['referenceCode']])
        tables.append(os_table)

        # Sizes
        preset_table = formatting.Table(['Size', 'Value'], title="Sizes")
        preset_table.sortby = 'Value'
        preset_table.align = 'l'

        for size in options['sizes']:
            preset_table.add_row([size['name'], size['key']])
        tables.append(preset_table)

        #  RAM
        ram_table = formatting.Table(['memory', 'Value'], title="RAM")
        ram_table.sortby = 'Value'
        ram_table.align = 'l'

        for ram in options['ram']:
            ram_table.add_row([ram['name'], ram['key']])
        tables.append(ram_table)

        # Data base
        database_table = formatting.Table(['database', 'Value'], title="Databases")
        database_table.sortby = 'Value'
        database_table.align = 'l'

        for database in options['database']:
            database_table.add_row([database['name'], database['key']])
        tables.append(database_table)

        # Guest_core
        guest_core_table = formatting.Table(['cpu', 'Value', 'Capacity'], title="Guest_core")
        guest_core_table.sortby = 'Value'
        guest_core_table.align = 'l'

        for guest_core in options['guest_core']:
            guest_core_table.add_row([guest_core['name'], guest_core['key'], guest_core['capacity']])
        tables.append(guest_core_table)

        # Guest_core
        guest_disk_table = formatting.Table(['guest_disk', 'Value', 'Capacity', 'Disk'], title="Guest_disks")
        guest_disk_table.sortby = 'Value'
        guest_disk_table.align = 'l'

        for guest_disk in options['guest_disk']:
            guest_disk_table.add_row(
                [guest_disk['name'], guest_disk['key'], guest_disk['capacity'], guest_disk['disk']])
        tables.append(guest_disk_table)

        # Port speed
        port_speed_table = formatting.Table(['network', 'Key'], title="Network Options")
        port_speed_table.sortby = 'Key'
        port_speed_table.align = 'l'

        for speed in options['port_speed']:
            port_speed_table.add_row([speed['name'], speed['key']])
        tables.append(port_speed_table)

    env.fout(formatting.listing(tables, separator='\n'))


def preset_prices_table(sizes, tables):
    """Shows Server Preset options prices.

    :param [] sizes: List of Hardware Server sizes.
    :param tables: Table formatting.
    """
    preset_table = formatting.Table(['Size', 'Value', 'Hourly', 'Monthly'], title="Sizes Prices")
    preset_table.sortby = 'Value'
    preset_table.align = 'l'
    for size in sizes:
        preset_table.add_row([size['name'], size['key'], "%.4f" % size['hourlyRecurringFee'],
                              "%.4f" % size['recurringFee']])
    tables.append(preset_table)


def os_prices_table(operating_systems, tables):
    """Shows Server Operating Systems prices cost and capacity restriction.

    :param [] operating_systems: List of Hardware Server operating systems.
    :param tables: Table formatting.
    """
    os_table = formatting.Table(['OS Key', 'Hourly', 'Monthly', 'Restriction'],
                                title="Operating Systems Prices")
    os_table.sortby = 'OS Key'
    os_table.align = 'l'
    for operating_system in operating_systems:
        for price in operating_system['prices']:
            cr_max = _get_price_data(price, 'capacityRestrictionMaximum')
            cr_min = _get_price_data(price, 'capacityRestrictionMinimum')
            cr_type = _get_price_data(price, 'capacityRestrictionType')
            os_table.add_row(
                [operating_system['key'],
                 _get_price_data(price, 'hourlyRecurringFee'),
                 _get_price_data(price, 'recurringFee'),
                 "%s - %s %s" % (cr_min, cr_max, cr_type)])
    tables.append(os_table)


def port_speed_prices_table(port_speeds, tables):
    """Shows Server Port Speeds prices cost and capacity restriction.

    :param [] port_speeds: List of Hardware Server Port Speeds.
    :param tables: Table formatting.
    """
    port_speed_table = formatting.Table(['Key', 'Speed', 'Hourly', 'Monthly', 'Restriction'],
                                        title="Network Options Prices")
    port_speed_table.sortby = 'Speed'
    port_speed_table.align = 'l'
    for speed in port_speeds:
        for price in speed['prices']:
            cr_max = _get_price_data(price, 'capacityRestrictionMaximum')
            cr_min = _get_price_data(price, 'capacityRestrictionMinimum')
            cr_type = _get_price_data(price, 'capacityRestrictionType')
            port_speed_table.add_row(
                [speed['key'], speed['speed'],
                 _get_price_data(price, 'hourlyRecurringFee'),
                 _get_price_data(price, 'recurringFee'),
                 "%s - %s %s" % (cr_min, cr_max, cr_type)])
    tables.append(port_speed_table)


def extras_prices_table(extras, tables):
    """Shows Server extras prices cost and capacity restriction.

    :param [] extras: List of Hardware Server Extras.
    :param tables: Table formatting.
    """
    extras_table = formatting.Table(['Extra Option Key', 'Hourly', 'Monthly', 'Restriction'],
                                    title="Extras Prices")
    extras_table.align = 'l'
    for extra in extras:
        for price in extra['prices']:
            cr_max = _get_price_data(price, 'capacityRestrictionMaximum')
            cr_min = _get_price_data(price, 'capacityRestrictionMinimum')
            cr_type = _get_price_data(price, 'capacityRestrictionType')
            extras_table.add_row(
                [extra['key'],
                 _get_price_data(price, 'hourlyRecurringFee'),
                 _get_price_data(price, 'recurringFee'),
                 "%s - %s %s" % (cr_min, cr_max, cr_type)])
    tables.append(extras_table)


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


def ram_prices_table(ram_list, tables):
    """Shows Server Port Speeds prices cost and capacity restriction.

    :param [] ram_list: List of Virtual Server Ram.
    :param tables: Table formatting.
    """
    ram_table = formatting.Table(['Key', 'Hourly', 'Monthly', 'Restriction'],
                                 title="Ram Prices")
    ram_table.sortby = 'Key'
    ram_table.align = 'l'
    for ram in ram_list:
        for price in ram['prices']:
            cr_max = _get_price_data(price, 'capacityRestrictionMaximum')
            cr_min = _get_price_data(price, 'capacityRestrictionMinimum')
            cr_type = _get_price_data(price, 'capacityRestrictionType')
            ram_table.add_row(
                [ram['key'],
                 _get_price_data(price, 'hourlyRecurringFee'),
                 _get_price_data(price, 'recurringFee'),
                 "%s - %s %s" % (cr_min, cr_max, cr_type)])
    tables.append(ram_table)


def database_prices_table(database_list, tables):
    """Shows Server Port Speeds prices cost and capacity restriction.

    :param [] database_list: List of Virtual Server database.
    :param tables: Table formatting.
    """
    database_table = formatting.Table(['Key', 'Hourly', 'Monthly', 'Restriction'],
                                      title="Data Base Prices")
    database_table.sortby = 'Key'
    database_table.align = 'l'
    for database in database_list:
        for price in database['prices']:
            cr_max = _get_price_data(price, 'capacityRestrictionMaximum')
            cr_min = _get_price_data(price, 'capacityRestrictionMinimum')
            cr_type = _get_price_data(price, 'capacityRestrictionType')
            database_table.add_row(
                [database['key'],
                 _get_price_data(price, 'hourlyRecurringFee'),
                 _get_price_data(price, 'recurringFee'),
                 "%s - %s %s" % (cr_min, cr_max, cr_type)])
    tables.append(database_table)


def guest_core_prices_table(guest_core_list, tables):
    """Shows Server Port Speeds prices cost and capacity restriction.

    :param [] guest_core_list: List of Virtual Server guest_core.
    :param tables: Table formatting.
    """
    guest_core_table = formatting.Table(['Key', 'Hourly', 'Monthly', 'Restriction'],
                                        title="Guest Core Prices")
    guest_core_table.sortby = 'Key'
    guest_core_table.align = 'l'
    for guest_core in guest_core_list:
        for price in guest_core['prices']:
            cr_max = _get_price_data(price, 'capacityRestrictionMaximum')
            cr_min = _get_price_data(price, 'capacityRestrictionMinimum')
            cr_type = _get_price_data(price, 'capacityRestrictionType')
            guest_core_table.add_row(
                [guest_core['key'],
                 _get_price_data(price, 'hourlyRecurringFee'),
                 _get_price_data(price, 'recurringFee'),
                 "%s - %s %s" % (cr_min, cr_max, cr_type)])
    tables.append(guest_core_table)


def guest_disk_prices_table(guest_disk_list, tables):
    """Shows Server Port Speeds prices cost and capacity restriction.

    :param [] guest_disk_list: List of Virtual Server guest_disk.
    :param tables: Table formatting.
    """
    guest_disk_table = formatting.Table(['Key', 'Hourly', 'Monthly', 'Restriction'],
                                        title="Guest Disk Prices")
    guest_disk_table.sortby = 'Key'
    guest_disk_table.align = 'l'
    for guest_disk in guest_disk_list:
        for price in guest_disk['prices']:
            cr_max = _get_price_data(price, 'capacityRestrictionMaximum')
            cr_min = _get_price_data(price, 'capacityRestrictionMinimum')
            cr_type = _get_price_data(price, 'capacityRestrictionType')
            guest_disk_table.add_row(
                [guest_disk['key'],
                 _get_price_data(price, 'hourlyRecurringFee'),
                 _get_price_data(price, 'recurringFee'),
                 "%s - %s %s" % (cr_min, cr_max, cr_type)])
    tables.append(guest_disk_table)


def _get_price_data(price, item):
    """Get a specific data from HS price.

    :param price: Hardware Server price.
    :param string item: Hardware Server price data.
    """
    result = '-'
    if item in price:
        result = price[item]
    return result
