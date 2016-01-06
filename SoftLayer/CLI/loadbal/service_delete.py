"""Deletes an existing load balancer service."""
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
    """Deletes an existing load balancer service."""

    mgr = SoftLayer.LoadBalancerManager(env.client)
    _, service_id = loadbal.parse_id(identifier)

    if not (env.skip_confirmations or
            formatting.confirm("This action will cancel a service from your "
                               "load balancer. Continue?")):
        raise exceptions.CLIAbort('Aborted.')

    mgr.delete_service(service_id)
    env.fout('Load balancer service %s is being cancelled!' % service_id)
