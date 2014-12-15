"""Unassigns a global IP from a target."""
# :license: MIT, see LICENSE for more details.

import softlayer
from softlayer.cli import environment
from softlayer.cli import helpers

import click


@click.command()
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """Unassigns a global IP from a target."""

    mgr = softlayer.NetworkManager(env.client)
    global_ip_id = helpers.resolve_id(mgr.resolve_global_ip_ids, identifier,
                                      name='global ip')
    mgr.unassign_global_ip(global_ip_id)
