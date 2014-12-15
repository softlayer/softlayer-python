"""Adds a load balancer given the id returned from create-options."""
# :license: MIT, see LICENSE for more details.

import softlayer
from softlayer.cli import environment
from softlayer.cli import exceptions
from softlayer.cli import formatting

import click


@click.command()
@click.argument('billing-id')
@click.option('--datacenter', '-d',
              help='Datacenter shortname (sng01, dal05, ...)')
@environment.pass_env
def cli(env, billing_id, datacenter):
    """Adds a load balancer given the id returned from create-options."""
    mgr = softlayer.LoadBalancerManager(env.client)

    if not formatting.confirm("This action will incur charges on your "
                              "account. Continue?"):
        raise exceptions.CLIAbort('Aborted.')
    mgr.add_local_lb(billing_id, datacenter=datacenter)
    return "Load balancer is being created!"
