"""Show load balancer options."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting


@click.command()
@environment.pass_env
def cli(env):
    """Get price options to create a load balancer with."""

    mgr = SoftLayer.LoadBalancerManager(env.client)

    table = formatting.Table(['price_id', 'capacity', 'description', 'price'])

    table.sortby = 'price'
    table.align['price'] = 'r'
    table.align['capacity'] = 'r'
    table.align['id'] = 'r'

    packages = mgr.get_lb_pkgs()

    for package in packages:
        table.add_row([
            package['prices'][0]['id'],
            package.get('capacity'),
            package['description'],
            '%.2f' % float(package['prices'][0]['recurringFee'])
        ])

    env.fout(table)
