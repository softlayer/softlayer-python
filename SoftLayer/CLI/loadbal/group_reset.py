"""Reset connections on a certain service group."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import loadbal


@click.command()
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """Reset connections on a certain service group."""
    mgr = SoftLayer.LoadBalancerManager(env.client)

    loadbal_id, group_id = loadbal.parse_id(identifier)

    mgr.reset_service_group(loadbal_id, group_id)
    env.fout('Load balancer service group connections are being reset!')
