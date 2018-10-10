"""Create a Reserved Capacity instance."""

import click


from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.managers.vs_capacity import CapacityManager as CapacityManager


@click.command(epilog=click.style("""WARNING: Reserved Capacity is on a yearly contract"""
                                  """ and not cancelable until the contract is expired.""", fg='red'))
@click.option('--name', '-n', required=True, prompt=True,
              help="Name for your new reserved capacity")
@click.option('--backend_router_id', '-b', required=True, prompt=True, type=int,
              help="backendRouterId, create-options has a list of valid ids to use.")
@click.option('--flavor', '-f', required=True, prompt=True,
              help="Capacity keyname (C1_2X2_1_YEAR_TERM for example).")
@click.option('--instances', '-i', required=True, prompt=True, type=int,
              help="Number of VSI instances this capacity reservation can support.")
@click.option('--test', is_flag=True,
              help="Do not actually create the virtual server")
@environment.pass_env
def cli(env, name, backend_router_id, flavor, instances, test=False):
    """Create a Reserved Capacity instance.

    *WARNING*: Reserved Capacity is on a yearly contract and not cancelable until the contract is expired.
    """
    manager = CapacityManager(env.client)

    result = manager.create(
        name=name,
        backend_router_id=backend_router_id,
        flavor=flavor,
        instances=instances,
        test=test)
    if test:
        table = formatting.Table(['Name', 'Value'], "Test Order")
        container = result['orderContainers'][0]
        table.add_row(['Name', container['name']])
        table.add_row(['Location', container['locationObject']['longName']])
        for price in container['prices']:
            table.add_row(['Contract', price['item']['description']])
        table.add_row(['Hourly Total', result['postTaxRecurring']])
    else:
        table = formatting.Table(['Name', 'Value'], "Reciept")
        table.add_row(['Order Date', result['orderDate']])
        table.add_row(['Order ID', result['orderId']])
        table.add_row(['status', result['placedOrder']['status']])
        table.add_row(['Hourly Total', result['orderDetails']['postTaxRecurring']])
    env.fout(table)
