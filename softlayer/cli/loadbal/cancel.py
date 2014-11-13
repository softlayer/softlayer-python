"""Cancel an existing load balancer."""
# :license: MIT, see LICENSE for more details.

import softlayer
from softlayer.cli import environment
from softlayer.cli import exceptions
from softlayer.cli import formatting
from softlayer.cli import loadbal

import click


@click.command()
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """Cancel an existing load balancer."""

    mgr = softlayer.LoadBalancerManager(env.client)

    _, loadbal_id = loadbal.parse_id(identifier)

    if any([env.skip_confirmations,
            formatting.confirm("This action will cancel a load balancer. "
                               "Continue?")]):
        mgr.cancel_lb(loadbal_id)
        return 'Load Balancer with id %s is being cancelled!' % identifier
    else:
        raise exceptions.CLIAbort('Aborted.')
