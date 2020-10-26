"""Verify or place an order."""
# :license: MIT, see LICENSE for more details.

import json

import click

from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer.managers import ordering

COLUMNS = ['keyName',
           'description',
           'cost', ]


@click.command()
@click.argument('package_keyname')
@click.argument('location')
@click.option('--preset',
              help="The order preset (if required by the package)")
@click.option('--verify',
              is_flag=True,
              help="Flag denoting whether or not to only verify the order, not place it")
@click.option('--quantity',
              type=int,
              default=1,
              help="The quantity of the item being ordered")
@click.option('--billing',
              type=click.Choice(['hourly', 'monthly']),
              default='hourly',
              show_default=True,
              help="Billing rate")
@click.option('--complex-type',
              help=("The complex type of the order. Starts with 'SoftLayer_Container_Product_Order'."))
@click.option('--extras',
              help="JSON string denoting extra data that needs to be sent with the order")
@click.argument('order_items', nargs=-1)
@environment.pass_env
def cli(env, package_keyname, location, preset, verify, billing, complex_type,
        quantity, extras, order_items):
    """Place or verify an order.

\b
1. Find the package keyName from `slcli order package-list`
2. Find the location from `slcli order package-locations PUBLIC_CLOUD_SERVER`
  If the package does not require a location, use 'NONE' instead.
3. Find the needed items `slcli order item-list PUBLIC_CLOUD_SERVER`
  Some packages, like PUBLIC_CLOUD_SERVER need presets, `slcli order preset-list PUBLIC_CLOUD_SERVER`
4. Find the complex type from https://sldn.softlayer.com/reference
5. Use that complex type to fill out any --extras

    Example::

        slcli order place --verify --preset B1_2X8X100 --billing hourly
        --complex-type SoftLayer_Container_Product_Order_Virtual_Guest
        --extras '{"virtualGuests": [{"hostname": "test", "domain": "ibm.com"}]}'
        PUBLIC_CLOUD_SERVER DALLAS13
        BANDWIDTH_0_GB_2 MONITORING_HOST_PING NOTIFICATION_EMAIL_AND_TICKET
        OS_DEBIAN_9_X_STRETCH_LAMP_64_BIT 1_IP_ADDRESS 1_IPV6_ADDRESS
        1_GBPS_PUBLIC_PRIVATE_NETWORK_UPLINKS REBOOT_REMOTE_CONSOLE
        AUTOMATED_NOTIFICATION UNLIMITED_SSL_VPN_USERS_1_PPTP_VPN_USER_PER_ACCOUNT

    """
    manager = ordering.OrderingManager(env.client)

    if extras:
        try:
            extras = json.loads(extras)
        except ValueError as err:
            raise exceptions.CLIAbort("There was an error when parsing the --extras value: {}".format(err))

    args = (package_keyname, location, order_items)
    kwargs = {'preset_keyname': preset,
              'extras': extras,
              'quantity': quantity,
              'complex_type': complex_type,
              'hourly': bool(billing == 'hourly')}

    if verify:
        table = formatting.Table(COLUMNS)
        order_to_place = manager.verify_order(*args, **kwargs)
        for price in order_to_place['orderContainers'][0]['prices']:
            cost_key = 'hourlyRecurringFee' if billing == 'hourly' else 'recurringFee'
            table.add_row([
                price['item']['keyName'],
                price['item']['description'],
                price[cost_key] if cost_key in price else formatting.blank()
            ])

    else:
        if not (env.skip_confirmations or formatting.confirm(
                "This action will incur charges on your account. Continue?")):
            raise exceptions.CLIAbort("Aborting order.")

        order = manager.place_order(*args, **kwargs)

        table = formatting.KeyValueTable(['name', 'value'])
        table.align['name'] = 'r'
        table.align['value'] = 'l'
        table.add_row(['id', order['orderId']])
        table.add_row(['created', order['orderDate']])
        table.add_row(['status', order['placedOrder']['status']])
    env.fout(table)
