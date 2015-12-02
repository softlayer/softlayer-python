"""Cancel an existing load balancer."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer.CLI import loadbal


@click.command()
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """Cancel an existing load balancer."""

    mgr = SoftLayer.LoadBalancerManager(env.client)

    _, loadbal_id = loadbal.parse_id(identifier)

    if not (env.skip_confirmations or
            formatting.confirm("This action will cancel a load balancer. "
                               "Continue?")):
        raise exceptions.CLIAbort('Aborted.')

    mgr.cancel_lb(loadbal_id)
    env.fout('Load Balancer with id %s is being cancelled!' % identifier)
