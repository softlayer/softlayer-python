"""Toggle the status of an existing load balancer service."""
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
    """Toggle the status of an existing load balancer service."""

    mgr = softlayer.LoadBalancerManager(env.client)
    _, service_id = loadbal.parse_id(identifier)

    if env.skip_confirmations or formatting.confirm("This action will toggle "
                                                    "the status on the "
                                                    "service. Continue?"):
        mgr.toggle_service_status(service_id)
        return 'Load balancer service %s status updated!' % identifier
    else:
        raise exceptions.CLIAbort('Aborted.')
