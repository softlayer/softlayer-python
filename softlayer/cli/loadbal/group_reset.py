"""Reset connections on a certain service group."""
# :license: MIT, see LICENSE for more details.

import softlayer
from softlayer.cli import environment
from softlayer.cli import loadbal

import click


@click.command()
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """Reset connections on a certain service group."""
    mgr = softlayer.LoadBalancerManager(env.client)

    loadbal_id, group_id = loadbal.parse_id(identifier)

    mgr.reset_service_group(loadbal_id, group_id)
    return 'Load balancer service group connections are being reset!'
