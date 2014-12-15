"""Cancel virtual servers."""
# :license: MIT, see LICENSE for more details.


import softlayer
from softlayer.cli import environment
from softlayer.cli import exceptions
from softlayer.cli import formatting
from softlayer.cli import helpers

import click


@click.command()
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """Cancel virtual servers."""

    vsi = softlayer.VSManager(env.client)
    vs_id = helpers.resolve_id(vsi.resolve_ids, identifier, 'VS')
    if env.skip_confirmations or formatting.no_going_back(vs_id):
        vsi.cancel_instance(vs_id)
    else:
        raise exceptions.CLIAbort('Aborted')
