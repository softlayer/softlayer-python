"""List active Load Balancer as a Service devices."""
import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer import utils


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


def location_sort(location):
    """Quick function that just returns the datacenter longName for sorting"""
    return utils.lookup(location, 'datacenter', 'longName')


def generate_lbaas_table(lbaas):
    """Takes a list of SoftLayer_Network_LBaaS_LoadBalancer and makes a table"""
    table = formatting.Table([
        'Id', 'Location', 'Name', 'Description', 'Public', 'Create Date', 'Members', 'Listeners'
    ], title="IBM Cloud LoadBalancer")

    table.align['Name'] = 'l'
    table.align['Description'] = 'l'
    table.align['Location'] = 'l'
    for this_lb in sorted(lbaas, key=location_sort):
        table.add_row([
            this_lb.get('id'),
            utils.lookup(this_lb, 'datacenter', 'longName'),
            this_lb.get('name'),
            this_lb.get('description'),
            'Yes' if this_lb.get('isPublic', 1) == 1 else 'No',
            utils.clean_time(this_lb.get('createDate')),
            this_lb.get('memberCount', 0),
            this_lb.get('listenerCount', 0)


        ])
    return table
