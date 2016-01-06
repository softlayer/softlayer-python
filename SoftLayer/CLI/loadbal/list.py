"""List active load balancers."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting


@click.command()
@environment.pass_env
def cli(env):
    """List active load balancers."""
    mgr = SoftLayer.LoadBalancerManager(env.client)

    load_balancers = mgr.get_local_lbs()

    table = formatting.Table(['ID',
                              'VIP Address',
                              'Location',
                              'SSL Offload',
                              'Connections/second',
                              'Type'])

    table.align['Connections/second'] = 'r'

    for load_balancer in load_balancers:
        ssl_support = 'Not Supported'
        if load_balancer['sslEnabledFlag']:
            if load_balancer['sslActiveFlag']:
                ssl_support = 'On'
            else:
                ssl_support = 'Off'
        lb_type = 'Standard'
        if load_balancer['dedicatedFlag']:
            lb_type = 'Dedicated'
        elif load_balancer['highAvailabilityFlag']:
            lb_type = 'HA'
        table.add_row([
            'local:%s' % load_balancer['id'],
            load_balancer['ipAddress']['ipAddress'],
            load_balancer['loadBalancerHardware'][0]['datacenter']['name'],
            ssl_support,
            load_balancer['connectionLimit'],
            lb_type
        ])

    env.fout(table)
