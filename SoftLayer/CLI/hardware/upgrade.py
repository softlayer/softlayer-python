"""Upgrade a hardware server."""
# :license: MIT, see LICENSE for more details.

import click
from SoftLayer import utils

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers


@click.command()
@click.argument('identifier')
@click.option('--memory', type=click.INT, help="Memory Size in GB")
@click.option('--network', help="Network port speed in Mbps",
              default=None,
              type=click.Choice(['100', '100 Redundant', '100 Dual',
                                 '1000', '1000 Redundant', '1000 Dual',
                                 '10000', '10000 Redundant', '10000 Dual'])
              )
@click.option('--drive-controller',
              help="Drive Controller",
              default=None,
              type=click.Choice(['Non-RAID', 'RAID']))
@click.option('--public-bandwidth', type=click.INT, help="Public Bandwidth in GB")
@click.option('--add-disk', nargs=2, multiple=True, type=(int, int),
              help="Add a Hard disk in GB to a specific channel, e.g 1000 GB in disk2, it will be "
                   "--add-disk 1000 2")
@click.option('--resize-disk', nargs=2, multiple=True, type=(int, int),
              help="Upgrade a specific disk size in GB, e.g --resize-disk 2000 2")
@click.option('--test', is_flag=True, default=False, help="Do not actually upgrade the hardware server")
@environment.pass_env
def cli(env, identifier, memory, network, drive_controller, public_bandwidth, add_disk, resize_disk, test):
    """Upgrade a Hardware Server."""

    mgr = SoftLayer.HardwareManager(env.client)
    table = formatting.KeyValueTable(['name', 'value'])
    table.align['name'] = 'r'
    table.align['value'] = 'l'

    if not any([memory, network, drive_controller, public_bandwidth, add_disk, resize_disk]):
        raise exceptions.ArgumentError("Must provide "
                                       " [--memory], [--network], [--drive-controller], [--public-bandwidth],"
                                       "[--add-disk] or [--resize-disk]")

    hw_id = helpers.resolve_id(mgr.resolve_ids, identifier, 'Hardware')
    if not test:
        if not (env.skip_confirmations or formatting.confirm(
                "This action will incur charges on your account. Continue?")):
            raise exceptions.CLIAbort('Aborted')

    disk_list = []
    if add_disk:
        for guest_disk in add_disk:
            disks = {'description': 'add_disk', 'capacity': guest_disk[0], 'number': guest_disk[1]}
            disk_list.append(disks)
    if resize_disk:
        for guest_disk in resize_disk:
            disks = {'description': 'resize_disk', 'capacity': guest_disk[0], 'number': guest_disk[1]}
            disk_list.append(disks)

    response = mgr.upgrade(hw_id, memory=memory, nic_speed=network, drive_controller=drive_controller,
                           public_bandwidth=public_bandwidth, disk=disk_list, test=test)

    if response:
        if test:
            add_data_to_table(response, table)
        else:
            table.add_row(['Order Date', response.get('orderDate')])
            table.add_row(['Order Id', response.get('orderId')])
            add_data_to_table(response['orderDetails'], table)
            place_order_table = get_place_order_information(response)
            table.add_row(['Place Order Information', place_order_table])
            order_detail_table = get_order_detail(response)
            table.add_row(['Order Detail (Billing Information)', order_detail_table])

    env.fout(table)


def add_data_to_table(response, table):
    """Add the hardware server upgrade result to the table"""
    table.add_row(['location', utils.lookup(response, 'locationObject', 'longName')])
    table.add_row(['quantity', response.get('quantity')])
    table.add_row(['Package Id', response.get('packageId')])
    table.add_row(['Currency Short Name', response.get('currencyShortName')])
    table.add_row(['Prorated Initial Charge', response.get('proratedInitialCharge')])
    table.add_row(['Prorated Order Total', response.get('proratedOrderTotal')])
    table.add_row(['Hourly Pricing', response.get('useHourlyPricing')])
    table_hardware = get_hardware_detail(response)
    table.add_row(['Hardware', table_hardware])
    table_prices = get_hardware_prices(response)
    table.add_row(['Prices', table_prices])


def get_place_order_information(response):
    """Get the hardware server place order information."""
    table_place_order = formatting.Table(['Id', 'Account Id', 'Status', 'Account CompanyName',
                                          'UserRecord FirstName', 'UserRecord LastName', 'UserRecord Username'])
    table_place_order.add_row([response.get('id'),
                               response.get('accountId'),
                               response.get('status'),
                               utils.lookup(response, 'account', 'companyName'),
                               utils.lookup(response, 'userRecord', 'firstName'),
                               utils.lookup(response, 'account', 'lastName'),
                               utils.lookup(response, 'account', 'username')])

    return table_place_order


def get_hardware_detail(response):
    """Get the hardware server detail."""
    table_hardware = formatting.Table(['Account Id', 'Hostname', 'Domain'])
    for hardware in response['hardware']:
        table_hardware.add_row([hardware.get('accountId'),
                                hardware.get('hostname'),
                                hardware.get('domain')])

    return table_hardware


def get_hardware_prices(response):
    """Get the hardware server prices."""
    table_prices = formatting.Table(['Id', 'HourlyRecurringFee', 'RecurringFee', 'Categories', 'Item Description',
                                     'Item Units'])
    for price in response['prices']:
        categories = price.get('categories')[0]
        table_prices.add_row([price.get('id'),
                              price.get('hourlyRecurringFee'),
                              price.get('recurringFee'),
                              categories.get('name'),
                              utils.lookup(price, 'item', 'description'),
                              utils.lookup(price, 'item', 'units')])

    return table_prices


def get_order_detail(response):
    """Get the hardware server order detail."""
    table_order_detail = formatting.Table(['Billing City', 'Billing Country Code', 'Billing Email',
                                           'Billing Name First', 'Billing Name Last', 'Billing Postal Code',
                                           'Billing State'])
    table_order_detail.add_row([utils.lookup(response, 'orderDetails', 'billingInformation', 'billingCity'),
                                utils.lookup(response, 'orderDetails', 'billingInformation', 'billingCountryCode'),
                                utils.lookup(response, 'orderDetails', 'billingInformation', 'billingEmail'),
                                utils.lookup(response, 'orderDetails', 'billingInformation', 'billingNameFirst'),
                                utils.lookup(response, 'orderDetails', 'billingInformation', 'billingNameLast'),
                                utils.lookup(response, 'orderDetails', 'billingInformation', 'billingPostalCode'),
                                utils.lookup(response, 'orderDetails', 'billingInformation', 'billingState')])

    return table_order_detail
