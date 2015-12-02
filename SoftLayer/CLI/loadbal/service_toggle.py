"""Toggle the status of an existing load balancer service."""
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
    """Toggle the status of an existing load balancer service."""

    mgr = SoftLayer.LoadBalancerManager(env.client)
    _, service_id = loadbal.parse_id(identifier)

    if not (env.skip_confirmations or
            formatting.confirm("This action will toggle the status on the "
                               "service. Continue?")):
        raise exceptions.CLIAbort('Aborted.')

    mgr.toggle_service_status(service_id)
    env.fout('Load balancer service %s status updated!' % identifier)
