"""Order/create a vwmare licenses."""
# :licenses: MIT, see LICENSE for more details.

import click
from SoftLayer.managers import ordering

from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting


@click.command()
@click.option('--key', '-k', required=True, prompt=True, help="The License Key for this specific Account License.")
@click.option('--datacenter', '-d', required=True, prompt=True, help="Datacenter shortname")
@environment.pass_env
def cli(env, key, datacenter):
    """Order/create a vlan instance."""

    complex_type = 'SoftLayer_Container_Product_Order_Software_License'
    item_package = [key]

    ordering_manager = ordering.OrderingManager(env.client)
    result = ordering_manager.place_order(package_keyname='SOFTWARE_LICENSE_PACKAGE',
                                          location=datacenter,
                                          item_keynames=item_package,
                                          complex_type=complex_type,
                                          hourly=False)
    table = formatting.KeyValueTable(['name', 'value'])
    table.align['name'] = 'r'
    table.align['value'] = 'l'
    table.add_row(['id', result['orderId']])
    table.add_row(['created', result['orderDate']])

    env.fout(table)
