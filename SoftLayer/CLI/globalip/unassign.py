"""Unassigns a global IP from a target."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import helpers

# pylint: disable=too-many-instance-attributes


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.argument('identifier')
@click.option('--details', help='Shows very detailed list of charges')
@environment.pass_env
def cli(env, identifier, details):
    """Unassigns a global IP from a target."""

    mgr = SoftLayer.NetworkManager(env.client)
    global_ip_id = helpers.resolve_id(mgr.resolve_global_ip_ids, identifier,
                                      name='global ip')
    mgr.unassign_global_ip(global_ip_id)
