"""Deletes an existing load balancer service group."""
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
    """Deletes an existing load balancer service group."""
    mgr = SoftLayer.LoadBalancerManager(env.client)

    _, group_id = loadbal.parse_id(identifier)

    if env.skip_confirmations or formatting.confirm("This action will cancel "
                                                    "a service group. "
                                                    "Continue?"):
        mgr.delete_service_group(group_id)
        return 'Service group %s is being deleted!' % identifier
    else:
        raise exceptions.CLIAbort('Aborted.')
