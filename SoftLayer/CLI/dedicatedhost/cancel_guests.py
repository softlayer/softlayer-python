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
@environment.pass_env
def cli(env, identifier):
    """Cancel all virtual guests of the dedicated host immediately"""

    dh_mgr = SoftLayer.DedicatedHostManager(env.client)
    vs_mgr = SoftLayer.VSManager(env.client)

    host_id = helpers.resolve_id(dh_mgr.resolve_ids, identifier, 'dedicated host')

    guests = dh_mgr.list_guests(host_id)

    if guests:
        msg = '%s guest(s) will be cancelled, ' \
              'do you want to continue?' % len(guests)

        if not (env.skip_confirmations or formatting.confirm(msg)):
            raise exceptions.CLIAbort('Aborted')

        for guest in guests:
            vs_mgr.cancel_instance(guest['id'])

        click.secho('All guests into the dedicated host %s were cancelled' % host_id, fg='green')

    else:
        click.secho('There is not any guest into the dedicated host %s' % host_id, fg='red')
