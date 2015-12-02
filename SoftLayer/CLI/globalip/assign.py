"""Assigns the global IP to a target."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import helpers


@click.command()
@click.argument('identifier')
@click.argument('target')
@environment.pass_env
def cli(env, identifier, target):
    """Assigns the global IP to a target."""

    mgr = SoftLayer.NetworkManager(env.client)
    global_ip_id = helpers.resolve_id(mgr.resolve_global_ip_ids, identifier,
                                      name='global ip')
    mgr.assign_global_ip(global_ip_id, target)
