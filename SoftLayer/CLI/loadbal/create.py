"""Adds a load balancer given the id returned from create-options."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting


@click.command()
@click.argument('billing-id')
@click.option('--datacenter', '-d',
              help='Datacenter shortname (sng01, dal05, ...)')
@environment.pass_env
def cli(env, billing_id, datacenter):
    """Adds a load balancer given the id returned from create-options."""
    mgr = SoftLayer.LoadBalancerManager(env.client)

    if not formatting.confirm("This action will incur charges on your "
                              "account. Continue?"):
        raise exceptions.CLIAbort('Aborted.')
    mgr.add_local_lb(billing_id, datacenter=datacenter)
    env.fout("Load balancer is being created!")
