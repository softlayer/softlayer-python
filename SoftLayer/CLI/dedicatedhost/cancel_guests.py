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
    """Cancel all virtual guests of the dedicated host immediately.

       Use the 'slcli vs cancel' command to cancel an specific guest
    """

    dh_mgr = SoftLayer.DedicatedHostManager(env.client)

    host_id = helpers.resolve_id(dh_mgr.resolve_ids, identifier, 'dedicated host')

    if not (env.skip_confirmations or formatting.no_going_back(host_id)):
        raise exceptions.CLIAbort('Aborted')

    table = formatting.Table(['id', 'server name', 'status'])

    result = dh_mgr.cancel_guests(host_id)

    if result:
        for status in result:
            table.add_row([
                status['id'],
                status['fqdn'],
                status['status']
            ])

        env.fout(table)
    else:
        click.secho('There is not any guest into the dedicated host %s' % host_id, fg='red')
