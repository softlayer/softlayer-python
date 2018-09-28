"""Create a Reserved Capacity instance. 


"""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.managers.vs_capacity import CapacityManager as CapacityManager


from pprint import pprint as pp

@click.command(epilog=click.style("""WARNING: Reserved Capacity is on a yearly contract"""
                                  """ and not cancelable until the contract is expired.""", fg='red'))
@click.option('--name', '-n', required=True, prompt=True,
              help="Name for your new reserved capacity")
@click.option('--datacenter', '-d', required=True, prompt=True,
              help="Datacenter shortname")
@click.option('--backend_router_id', '-b', required=True, prompt=True,
              help="backendRouterId, create-options has a list of valid ids to use.")
@click.option('--capacity', '-c', required=True, prompt=True,
              help="Capacity keyname (C1_2X2_1_YEAR_TERM for example).")
@click.option('--quantity', '-q', required=True, prompt=True,
              help="Number of VSI instances this capacity reservation can support.")
@click.option('--test', is_flag=True,
              help="Do not actually create the virtual server")
@environment.pass_env
def cli(env, name, datacenter, backend_router_id, capacity, quantity, test=False):
    """Create a Reserved Capacity instance. *WARNING*: Reserved Capacity is on a yearly contract and not cancelable until the contract is expired."""
    manager = CapacityManager(env.client)
    result = manager.create(
        name=name,
        datacenter=datacenter,
        backend_router_id=backend_router_id,
        capacity=capacity,
        quantity=quantity,
        test=test)

    pp(result)
    if test:
        table = formating.Table(['Name', 'Value'], "Test Order")
        container = result['orderContainers'][0]
        table.add_row(['Name', container['name']])
        table.add_row(['Location'], container['locationObject']['longName'])
        for price in container['prices']:
            table.add_row([price['item']['keyName'], price['item']['description']])
        table.add_row(['Total', result['postTaxRecurring']])
    else:
        table = formatting.Table(['Name', 'Value'], "Reciept")
        table.add_row(['Order Date', result['orderDate']])
        table.add_row(['Order ID', result['orderId']])
        table.add_row(['status', result['placedOrder']['status']])
        for item in result['placedOrder']['items']:
            table.add_row([item['categoryCode'], item['description']])
        table.add_row(['Total', result['orderDetails']['postTaxRecurring']])
    env.fout(table)


"""
Calling: SoftLayer_Product_Order::placeOrder(
id=None, 
mask='', 
filter='None', 
args=(
    {'orderContainers': [
        {'backendRouterId': 1079095, 
        'name': 'cgallo-test-capacity', 
        'quantity': 1, 
        'packageId': 1059, 
        'location': 1854895, 
        'useHourlyPricing': True, 
        'complexType': 'SoftLayer_Container_Product_Order_Virtual_ReservedCapacity', 
        'prices': [{'id': 217633}]}]},), limit=None, offset=None))
Resetting dropped connection: r237377.application.qadal0501.softlayer.local
"""