"""Cancel virtual servers."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """Cancel virtual servers."""

    vsi = SoftLayer.VSManager(env.client)
    vs_id = helpers.resolve_id(vsi.resolve_ids, identifier, 'VS')
    if not (env.skip_confirmations or formatting.no_going_back(vs_id)):
        raise exceptions.CLIAbort('Aborted')

    virtual_server = vsi.cancel_instance(vs_id)

    if virtual_server:
        env.fout("The virtual server instance: {} was cancelled.".format(vs_id))
