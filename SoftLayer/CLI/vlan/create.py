"""Order/create a VLAN instance."""
# :license: MIT, see LICENSE for more details.

import click
from SoftLayer.managers import ordering

from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting


@click.command()
@click.option('--name', required=False, prompt=True, help="Vlan name")
@click.option('--datacenter', '-d', required=True, prompt=True, help="Datacenter shortname")
@click.option('--network', default='public', show_default=True, type=click.Choice(['public', 'private']),
              help='Network vlan type')
@click.option('--billing', default='hourly', show_default=True, type=click.Choice(['hourly', 'monthly']),
              help="Billing rate")
@environment.pass_env
def cli(env, name, datacenter, network, billing):
    """Order/create a VLAN instance."""

    item_package = ['PUBLIC_NETWORK_VLAN']
    complex_type = 'SoftLayer_Container_Product_Order_Network_Vlan'
    if not network:
        item_package = ['PRIVATE_NETWORK_VLAN']

    ordering_manager = ordering.OrderingManager(env.client)
    result = ordering_manager.place_order(package_keyname='NETWORK_VLAN',
                                          location=datacenter,
                                          item_keynames=item_package,
                                          complex_type=complex_type,
                                          hourly=billing,
                                          extras={'name': name})
    table = formatting.KeyValueTable(['name', 'value'])
    table.align['name'] = 'r'
    table.align['value'] = 'l'
    table.add_row(['id', result['orderId']])
    table.add_row(['created', result['orderDate']])

    env.fout(table)
