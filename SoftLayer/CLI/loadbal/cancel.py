"""Cancel an existing load balancer."""
# :license: MIT, see LICENSE for more details.

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer.CLI import loadbal

import click


@click.command()
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """Cancel an existing load balancer."""

    mgr = SoftLayer.LoadBalancerManager(env.client)

    _, loadbal_id = loadbal.parse_id(identifier)

    if any([env.skip_confirmations,
            formatting.confirm("This action will cancel a load balancer. "
                               "Continue?")]):
        mgr.cancel_lb(loadbal_id)
        return 'Load Balancer with id %s is being cancelled!' % identifier
    else:
        raise exceptions.CLIAbort('Aborted.')
