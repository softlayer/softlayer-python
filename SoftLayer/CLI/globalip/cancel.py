"""Cancel global IP"""
# :license: MIT, see LICENSE for more details.

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers

import click


@click.command()
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """Cancel global IP"""

    mgr = SoftLayer.NetworkManager(env.client)
    global_ip_id = helpers.resolve_id(mgr.resolve_global_ip_ids, identifier,
                                      name='global ip')

    if env.skip_confirmations or formatting.no_going_back(global_ip_id):
        mgr.cancel_global_ip(global_ip_id)
    else:
        raise exceptions.CLIAbort('Aborted')
