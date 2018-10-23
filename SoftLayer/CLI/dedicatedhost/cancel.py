"""Cancel a dedicated host."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers


@click.command()
@click.argument('identifier')
@click.option('--immediate',
              is_flag=True,
              default=False,
              help="Cancels the dedicated host immediately (instead of on the billing anniversary)")
@environment.pass_env
def cli(env, identifier, immediate):
    """Cancel a dedicated host server."""

    mgr = SoftLayer.DedicatedHostManager(env.client)

    host_id = helpers.resolve_id(mgr.resolve_ids, identifier, 'dedicated host')

    if not (env.skip_confirmations or formatting.no_going_back(host_id)):
        raise exceptions.CLIAbort('Aborted')

    mgr.cancel_host(host_id, immediate)

    click.secho('Dedicated Host %s was successfully cancelled' % host_id, fg='green')
