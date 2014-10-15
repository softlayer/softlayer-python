"""Deletes an existing load balancer service"""
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
    """Deletes an existing load balancer service"""

    mgr = SoftLayer.LoadBalancerManager(env.client)
    _, service_id = loadbal.parse_id(identifier)

    if env.skip_confirmations or formatting.confirm("This action will cancel "
                                                    "a service from your load "
                                                    "balancer. Continue?"):
        mgr.delete_service(service_id)
        return 'Load balancer service %s is being cancelled!' % service_id
    else:
        raise exceptions.CLIAbort('Aborted.')
