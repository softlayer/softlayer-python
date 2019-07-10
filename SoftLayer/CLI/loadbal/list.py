"""List active Load Balancer as a Service devices."""
import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer import utils
from pprint import pprint as pp 

@click.command()
@environment.pass_env
def cli(env):
    """List active Load Balancer as a Service devices."""
    mgr = SoftLayer.LoadBalancerManager(env.client)

    lbaas = mgr.get_lbaas()
    if lbaas:
        lbaas_table = generate_lbaas_table(lbaas)
        env.fout(lbaas_table)

    else:
        env.fout("No LBaaS devices found")


def location_sort(x):
    """Quick function that just returns the datacenter longName for sorting"""
    return utils.lookup(x, 'datacenter', 'longName')


def generate_lbaas_table(lbaas):
    """Takes a list of SoftLayer_Network_LBaaS_LoadBalancer and makes a table"""
    table = formatting.Table([
        'Id', 'Location', 'Address', 'Description', 'Public', 'Create Date', 'Members', 'Listeners'
    ], title="IBM Cloud LoadBalancer")

    table.align['Address'] = 'l'
    table.align['Description'] = 'l'
    table.align['Location'] = 'l'
    for lb in sorted(lbaas,key=location_sort):
        table.add_row([
            lb.get('id'),
            utils.lookup(lb, 'datacenter', 'longName'),
            lb.get('address'),
            lb.get('description'),
            'Yes' if lb.get('isPublic', 1) == 1 else 'No',
            utils.clean_time(lb.get('createDate')),
            lb.get('memberCount', 0),
            lb.get('listenerCount', 0)


        ])
    return table

